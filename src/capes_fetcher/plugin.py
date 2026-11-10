"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
import email.utils
import json
import os
from pathlib import Path
from typing import Any

import typer
from quantilica.cli.sdk import (
    CheckPlanItem,
    FetcherApp,
    default_client,
    make_resolve_groups,
)
from quantilica.cli.ui import get_console
from quantilica.core.http import HttpClient, HttpStatusError
from quantilica.core.manifests import manifest_sidecar_path
from quantilica.core.registry import FetcherInfo
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, catalog_rows, list_datasets
from .storage import DataRepository

console = get_console()


def _out(text: str) -> None:
    """Imprime texto literal no console Rich compartilhado (sem markup/quebra)."""
    console.print(text, markup=False, highlight=False, emoji=False, soft_wrap=True)


# O SDK espera ``alias -> lista de grupos`` (string crua viraria ``list("x")``).
ALIASES: dict[str, list[str]] = GROUP_ALIASES
resolve_groups = make_resolve_groups(GROUPS, ALIASES)


def ckan_modified(entry: dict[str, Any]) -> dt.datetime | None:
    """``last_modified`` do recurso no CKAN (``remote_modified``), em UTC.

    O CKAN publica ISO 8601 sem fuso (UTC). Valores ausentes ou ilegíveis
    retornam ``None``.
    """
    raw = entry.get("remote_modified")
    if not raw:
        return None
    try:
        value = dt.datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value.astimezone(dt.UTC)


def _ckan_size(entry: dict[str, Any]) -> int | None:
    """Tamanho em bytes do recurso no CKAN, ou ``None`` se ausente/inválido."""
    try:
        size = int(entry.get("remote_size"))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return size if size > 0 else None


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Caminho local de uma entry.

    O carimbo é a data real do arquivo (``Last-Modified`` do HEAD) quando ela
    é informada; senão, a data do CKAN (``remote_modified``, que viaja na entry
    e sobrevive ao plano JSON); só em último caso, hoje. Assim o HEAD falho não
    gera ``@<hoje>``.
    """
    stamp = last_modified
    if stamp is None:
        ckan = ckan_modified(entry)
        stamp = ckan.date() if ckan is not None else None
    return DataRepository(output_dir).path_for_entry(entry, last_modified=stamp)


# Servidor da CAPES responde 503 com frequência sob carga: mais tentativas e
# espera maior entre elas que o padrão do SDK (sobrescrevível pelo ambiente).
DEFAULT_WORKERS = 2
DOWNLOAD_ATTEMPTS = 8
DOWNLOAD_RETRY_DELAY = 10.0


def _build_client() -> HttpClient:
    client = default_client()
    if "QUANTILICA_HTTP_ATTEMPTS" not in os.environ:
        client.attempts = max(client.attempts, DOWNLOAD_ATTEMPTS)
    if "QUANTILICA_HTTP_RETRY_DELAY" not in os.environ:
        client.retry_base_delay = max(client.retry_base_delay, DOWNLOAD_RETRY_DELAY)
    return client


fetcher = FetcherApp(
    name="capes",
    help="Coletor e conversor Lake Hive de dados da pós-graduação e teses da CAPES",
    info=FetcherInfo(
        id="capes",
        nome="CAPES - Pós-Graduação e Teses",
        orgao="Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES)",
        licenca="Creative Commons Atribuição (CC BY)",
        homepage="https://dadosabertos.capes.gov.br",
        cadencia="yearly",
        dominio="educacao",
    ),
    groups_dict=GROUPS,
    aliases_dict=ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/capes"),
    client=_build_client(),
    freshness_policy=FreshnessPolicy.HEAD_FALLBACK_GET,
)


def _http_date(moment: dt.datetime) -> str:
    return email.utils.format_datetime(moment, usegmt=True)


def _probe_head(url: str) -> Any:
    """HEAD rápido (poucas tentativas) para recursos sem tamanho no CKAN."""
    with HttpClient(timeout=30.0, attempts=2, retry_base_delay=1.0) as client:
        return client.head(url)


def _capes_check_entry(entry: dict[str, Any], output_dir: Path) -> CheckPlanItem:
    """Veredito de frescor com um HEAD curto por recurso.

    O HEAD (2 tentativas, 30 s) fornece tamanho, ETag e ``Last-Modified``; o
    carimbo do caminho é a data do ``Last-Modified``, como no download. Se o
    HEAD falhar, valem tamanho e data do CKAN (``remote_modified``): o caminho
    continua estável e a ação é ``download``. Sem nenhum dos dois, cai no check
    genérico do SDK.
    """
    ckan = ckan_modified(entry)
    dataset = str(entry.get("group") or entry.get("id") or "datasets")
    try:
        head = _probe_head(str(entry["url"]))
    except HttpStatusError as exc:
        if exc.status_code == 404:
            local = path_builder(output_dir, entry, None)
            return _item(
                entry,
                dataset,
                local,
                local.exists(),
                None,
                None,
                None,
                "skip-unavailable",
                "remote-404",
            )  # noqa: E501
        failure = f"metadata-unavailable: {exc}"
    except Exception as exc:  # noqa: BLE001 - metadata best effort
        failure = f"metadata-unavailable: {exc}"
    else:
        raw_lm = head.headers.get("Last-Modified")
        try:
            size = int(head.headers.get("Content-Length") or 0) or None
        except ValueError:
            size = None
        local = path_builder(output_dir, entry, _parse_http_date(raw_lm))
        exists = local.exists() or manifest_sidecar_path(local).exists()
        action, reason = (
            ("skip-up-to-date", "local-fresh")
            if exists
            else ("download", "not-present")
        )
        return _item(
            entry,
            dataset,
            local,
            exists,
            head.headers.get("ETag"),
            size,
            raw_lm,
            action,
            reason,
        )  # noqa: E501

    if ckan is None:
        return FetcherApp.check_entry(fetcher, entry, output_dir)
    local = path_builder(output_dir, entry, None)
    exists = local.exists() or manifest_sidecar_path(local).exists()
    return _item(
        entry,
        dataset,
        local,
        exists,
        None,
        _ckan_size(entry),
        _http_date(ckan),
        "download",
        failure,
    )  # noqa: E501


def _parse_http_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return email.utils.parsedate_to_datetime(value).astimezone(dt.UTC).date()
    except (TypeError, ValueError):
        return None


def _item(
    entry: dict[str, Any],
    dataset: str,
    local: Path,
    exists: bool,
    etag: str | None,
    size: int | None,
    last_modified: str | None,
    action: str,
    reason: str,
) -> CheckPlanItem:
    partition = str(entry["year"]) if entry.get("year") else None
    return CheckPlanItem(
        dataset=dataset,
        id=str(entry.get("id", "unknown")),
        url=str(entry["url"]),
        partition=partition,
        local_path=str(local),
        remote_etag=etag,
        remote_last_modified=last_modified,
        remote_size=size,
        local_exists=exists,
        action=action,
        reason=reason,
        entry=dict(entry),
    )


fetcher.check_entry = _capes_check_entry  # type: ignore[method-assign]


def _default_sync_workers(workers: int) -> None:
    """Muda o padrão de ``--workers`` do ``sync`` (o servidor limita a carga)."""
    for command in fetcher.app.registered_commands:
        callback = command.callback
        if command.name == "sync" and callback is not None:
            if callback.__defaults__ is None:
                continue
            code = callback.__code__
            names = code.co_varnames[: code.co_argcount]
            defaults = list(callback.__defaults__)
            offset = len(names) - len(defaults)
            if "workers" in names:
                defaults[names.index("workers") - offset] = workers
                callback.__defaults__ = tuple(defaults)


_default_sync_workers(DEFAULT_WORKERS)


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte arquivos brutos de capes para o lake Hive (Parquet)."""
    try:
        from capes_fetcher import lake
    except ImportError as exc:
        raise ImportError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install capes --extra analysis"
        ) from exc
    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


def catalogo(
    grupo: str | None = typer.Argument(None, help="Grupo, alias ou macro-alias"),
    tier: str | None = typer.Option(None, help="r1 (baixa hoje) ou listed"),
    as_json: bool = typer.Option(False, "--json", help="Saída em JSON"),
) -> None:
    """Mostra o catálogo completo de pacotes (R1 e listados, sem rede)."""
    rows = catalog_rows(grupo, tier)
    if as_json:
        _out(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for row in rows:
        _out(
            f"{row['group']:<21} {row['tier']:<6} "
            f"{row['era_start']}-{row['era_end']} csv={row['n_csv']:<3} {row['slug']}"
        )
    n_r1 = sum(1 for r in rows if r["tier"] == "r1")
    _out(f"\n{len(rows)} pacote(s): {n_r1} R1, {len(rows) - n_r1} listados.")


def discover_cmd(
    as_json: bool = typer.Option(False, "--json", help="Saída em JSON"),
    fail_on_change: bool = typer.Option(
        False, "--fail-on-change", help="Sai com código 1 se houver novidade"
    ),
) -> None:
    """Detecta pacotes novos ou removidos no CKAN da CAPES (servidor lento)."""
    from .discover import discover

    report = discover()
    if as_json:
        _out(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        _out(f"{report.known} pacote(s) do catálogo encontrados no CKAN.")
        for pkg in report.new_packages:
            _out(f"NOVO     {pkg['slug']}")
        for slug in report.removed_packages:
            _out(f"REMOVIDO NA FONTE {slug} (bruto mantido)")
        if not report.has_changes:
            _out("Sem novidades em relação ao catálogo.")
    if fail_on_change and report.has_changes:
        raise typer.Exit(1)


fetcher.attach_command(catalogo, name="catalogo")
fetcher.attach_command(discover_cmd, name="discover")
fetcher.command_convert(convert)
fetcher.command_pipeline(convert)


app = fetcher.app
