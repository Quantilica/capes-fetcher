"""Tests for CapesClient."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from quantilica.core.manifests import DownloadManifest

from capes_fetcher.client import CapesClient


def test_client_init() -> None:
    client = CapesClient()
    assert client.client is not None
    assert "capes.gov.br" in client.base_url


def test_package_show() -> None:
    client = CapesClient()
    mock_pkg = {"id": "pkg-1", "title": "Teses 2024", "resources": []}
    with patch.object(client.ckan, "package_show", return_value=mock_pkg):
        res = client.package_show("pkg-1")
        assert res["id"] == "pkg-1"


def test_search_packages() -> None:
    client = CapesClient()
    mock_pkgs = [{"id": "pkg-1"}, {"id": "pkg-2"}]
    with patch.object(client.ckan, "iter_packages", return_value=iter(mock_pkgs)):
        res = client.search_packages("teses")
        assert len(res) == 2


def test_pick_package_resources() -> None:
    client = CapesClient()
    pkg = {
        "resources": [
            {"name": "dados_2024", "format": "XLSX", "url": "https://.../1.xlsx"},
            {"name": "dados_2024", "format": "CSV", "url": "https://.../1.csv"},
        ]
    }
    picked = client.pick_package_resources(pkg)
    assert len(picked) == 1
    assert picked[0]["format"] == "CSV"


def test_download_resource(tmp_path) -> None:
    client = CapesClient()
    target = tmp_path / "dados_2024.csv"
    mock_manifest = MagicMock(spec=DownloadManifest)
    with patch.object(
        client.client, "download_with_manifest", return_value=mock_manifest
    ):
        res = client.download_resource("https://example.com/test.csv", target)
        assert res == mock_manifest
