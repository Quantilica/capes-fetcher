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
    """Caminho local de uma entry, carimbado pela data do CKAN.

    A data de ``remote_modified`` (que viaja na entry, inclusive pelo plano
    JSON) tem precedência sobre ``last_modified`` do HEAD: o caminho é o mesmo
    no ``check`` e no download, e não vira ``@hoje`` quando o HEAD falha.
    """
    ckan = ckan_modified(entry)
    stamp = ckan.date() if ckan is not None else last_modified
    return DataRepository(output_dir).path_for_entry(entry, last_modified=stamp)


# Servidor da CAPES responde 503 com frequência sob carga: mais tentativas e
# espera maior entre elas que o padrão do SDK (sobrescrevível pelo ambiente).
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
    """Veredito de frescor a partir dos metadados do CKAN, sem HEAD.

    O ``package_show`` já traz ``size`` e ``last_modified`` de cada recurso
    (iguais a ``Content-Length`` e ``Last-Modified`` do HEAD). Com os dois, o
    item sai sem rede. Quando falta o tamanho, um HEAD curto o completa (e o
    ETag); se o HEAD falhar, o item sai com o carimbo do CKAN, caminho estável
    e ação ``download``. Sem ``remote_modified`` cai no check genérico do SDK.
    """
    modified = ckan_modified(entry)
    if modified is None:
        return FetcherApp.check_entry(fetcher, entry, output_dir)

    dataset = str(entry.get("group") or entry.get("id") or "datasets")
    local = path_builder(output_dir, entry, None)
    exists = local.exists() or manifest_sidecar_path(local).exists()
    size = _ckan_size(entry)
    etag: str | None = None
    last_modified = _http_date(modified)
    reason_suffix = ""
    if size is None:
        try:
            head = _probe_head(str(entry["url"]))
        except HttpStatusError as exc:
            if exc.status_code == 404:
                return _item(
                    entry,
                    dataset,
                    local,
                    exists,
                    None,
                    None,
                    last_modified,
                    "skip-unavailable",
                    "remote-404",
                )
            reason_suffix = f"metadata-unavailable: {exc}"
        except Exception as exc:  # noqa: BLE001 - metadata best effort
            reason_suffix = f"metadata-unavailable: {exc}"
        else:
            etag = head.headers.get("ETag")
            try:
                size = int(head.headers.get("Content-Length") or 0) or None
            except ValueError:
                size = None
    if reason_suffix:
        return _item(
            entry,
            dataset,
            local,
            exists,
            None,
            None,
            last_modified,
            "download",
            reason_suffix,
        )
    if exists:
        action, reason = "skip-up-to-date", "ckan-fresh"
    else:
        action, reason = "download", "not-present"
    return _item(
        entry, dataset, local, exists, etag, size, last_modified, action, reason
    )


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
