"""HTTP and CKAN client for CAPES open data."""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from quantilica.core.ckan import CkanClient, pick_resources
from quantilica.core.http import HttpClient, resolve_verify_from_env
from quantilica.core.logging import get_logger
from quantilica.core.storage import ExpectedFormat, expected_format_for_path

from .constants import CAPES_CKAN_URL

logger = get_logger(__name__)

# O servidor da CAPES é lento (``package_list`` levou mais de 2 minutos em
# 2026-11-03): a descoberta pede ao menos 300 s por requisição, salvo se a
# operação fixou ``QUANTILICA_HTTP_TIMEOUT``.
CATALOG_TIMEOUT = 300.0


def _default_http_client() -> HttpClient:
    """Cliente padrão do host (``QUANTILICA_HTTP_*``, SSL, CA), com plano B do core."""
    try:
        from quantilica.cli.sdk import default_client
    except ImportError:  # CLI autônoma, sem o host instalado
        client = HttpClient(verify=resolve_verify_from_env(), emulate_browser=True)
    else:
        client = default_client()
    if "QUANTILICA_HTTP_TIMEOUT" not in os.environ:
        client.timeout = max(client.timeout, CATALOG_TIMEOUT)
    return client


def _resource_key(resource: dict[str, Any]) -> str:
    """Nome lógico do recurso, como o ``pick_resources`` do core o agrupa."""
    return str(resource.get("name") or resource.get("id") or "").strip()


class CapesClient:
    """Client for discovering and downloading CAPES datasets via CKAN."""

    def __init__(
        self,
        *,
        base_url: str = CAPES_CKAN_URL,
        client: HttpClient | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or _default_http_client()
        self.logger = logger or get_logger(__name__)
        self.ckan = CkanClient(base_url, client=self.client, logger=self.logger)

    def package_show(self, package_id: str) -> dict[str, Any]:
        """Fetch package details from CAPES CKAN."""
        return self.ckan.package_show(package_id)

    def package_names(self) -> list[str]:
        """Lista os nomes de todos os pacotes (``package_list``).

        O servidor da CAPES é lento (mais de 2 minutos nesta chamada em
        2026-11-03); o timeout do cliente é de 300 s.
        """
        response = self.client.get(f"{self.base_url}/api/3/action/package_list")
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(f"package_list falhou: {payload.get('error')}")
        return [str(name) for name in payload["result"]]

    def search_packages(
        self, q: str | None = None, rows: int = 1000
    ) -> list[dict[str, Any]]:
        """Search CAPES CKAN packages."""
        return list(self.ckan.iter_packages(q=q, rows=rows))

    def pick_package_resources(
        self,
        package: dict[str, Any],
        *,
        prefer: Sequence[str] = ("CSV", "ZIP"),
    ) -> list[dict[str, Any]]:
        """Pick best resources from package, prioritizing CSV/ZIP over XLSX.

        O core agrupa os recursos só pelo ``name`` do CKAN e fica com um por
        nome. Se dois recursos de formato baixável (``prefer``) e URLs
        diferentes dividem o mesmo nome, um deles deixa de ser coletado: a
        fusão é avisada em WARNING com os dois (a escolha não muda). O recurso
        de outro formato com o mesmo nome (o XLSX que duplica o CSV) é a
        deduplicação esperada e só vai a DEBUG.
        """
        chosen = pick_resources(package, prefer=prefer, dedupe_by_name=True)
        self._warn_merged_resources(package, chosen, prefer)
        return chosen

    def _warn_merged_resources(
        self,
        package: dict[str, Any],
        chosen: list[dict[str, Any]],
        prefer: Sequence[str],
    ) -> None:
        """Avisa os recursos descartados por dividirem o nome com o escolhido."""
        wanted = {fmt.upper() for fmt in prefer}
        by_name: dict[str, dict[str, Any]] = {_resource_key(r): r for r in chosen}
        for resource in package.get("resources") or []:
            winner = by_name.get(_resource_key(resource))
            if winner is None or winner is resource:
                continue
            if str(resource.get("url") or "") == str(winner.get("url") or ""):
                continue
            fmt = str(resource.get("format") or "").strip().upper()
            winner_fmt = str(winner.get("format") or "").strip().upper()
            level = (
                logging.WARNING
                if fmt in wanted and winner_fmt in wanted
                else logging.DEBUG
            )
            self.logger.log(
                level,
                "pacote %s: dois recursos com o nome %r e URLs diferentes; "
                "coletado %s (%s), descartado %s (%s)",
                package.get("name") or package.get("id") or "?",
                _resource_key(resource),
                winner.get("url"),
                winner_fmt or "?",
                resource.get("url"),
                fmt or "?",
            )

    def download_resource(
        self,
        url: str,
        dest: Path,
        *,
        dataset_id: str,
        source_id: str = "capes",
        producer: str = "capes-fetcher",
        force: bool = False,
        expected_format: ExpectedFormat | None = None,
    ) -> Path:
        """Baixa um recurso com manifesto lateral (``<dest>.manifest.json``).

        O formato esperado sai da extensão de ``dest`` quando não é informado, e
        a assinatura do conteúdo é conferida antes de gravar (HTML de bloqueio
        com HTTP 200 não substitui o arquivo).

        Returns:
            Path: O caminho do arquivo baixado (ou já em dia).
        """
        return self.client.download_with_manifest(
            url,
            dest,
            source_id=source_id,
            dataset_id=dataset_id,
            producer=producer,
            force=force,
            expected_format=expected_format or expected_format_for_path(dest),
        )
