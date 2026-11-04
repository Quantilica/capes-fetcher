"""HTTP and CKAN client for CAPES open data."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from quantilica.core.ckan import CkanClient, pick_resources
from quantilica.core.http import HttpClient
from quantilica.core.logging import get_logger
from quantilica.core.manifests import DownloadManifest

from .constants import CAPES_CKAN_URL

logger = get_logger(__name__)


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
        self.client = client or HttpClient(timeout=300.0)
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
        """Pick best resources from package, prioritizing CSV/ZIP over XLSX."""
        return pick_resources(package, prefer=prefer, dedupe_by_name=True)

    def download_resource(
        self,
        url: str,
        dest: Path,
        *,
        manifest_path: Path | None = None,
    ) -> DownloadManifest:
        """Download single resource with manifest sidecar."""
        return self.client.download_with_manifest(
            url,
            dest,
            manifest_path=manifest_path,
        )
