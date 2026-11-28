"""Tests for CapesClient."""

from __future__ import annotations

import io
import json
import logging
import zipfile
from pathlib import Path
from unittest.mock import patch

import httpx2
import pytest
from quantilica.core.exceptions import CorruptPayloadError
from quantilica.core.http import HttpClient

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


def _zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("dados.csv", "a;b\n1;2\n")
    return buf.getvalue()


def _client_with(handler) -> CapesClient:
    http = HttpClient(
        attempts=1, retry_base_delay=0.0, transport=httpx2.MockTransport(handler)
    )
    return CapesClient(client=http)


def test_download_resource_real_sem_mock_do_core(tmp_path: Path) -> None:
    """A assinatura chama o ``download_with_manifest`` de verdade (sem mock)."""
    body = b"coluna;valor\n1;2\n"

    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200,
            content=body,
            headers={"Last-Modified": "Wed, 01 Jan 2025 00:00:00 GMT"},
        )

    client = _client_with(handler)
    target = tmp_path / "dados_2024.csv"
    path = client.download_resource(
        "https://capes.test/dados_2024.csv", target, dataset_id="teses_2024"
    )
    assert path == target
    assert target.read_bytes() == body
    manifest = json.loads((tmp_path / "dados_2024.csv.manifest.json").read_text())
    assert manifest["source_id"] == "capes"
    assert manifest["dataset_id"] == "teses_2024"
    assert manifest["producer"] == "capes-fetcher"


def test_download_resource_zip_valido(tmp_path: Path) -> None:
    payload = _zip_bytes()
    client = _client_with(lambda request: httpx2.Response(200, content=payload))
    target = tmp_path / "x.zip"
    client.download_resource("https://capes.test/x.zip", target, dataset_id="d")
    assert zipfile.is_zipfile(target)


def test_download_resource_rejeita_html_de_bloqueio(tmp_path: Path) -> None:
    """HTML com 200 no lugar do ZIP não grava o arquivo."""
    html = b"<html><body>Acesso bloqueado</body></html>"
    client = _client_with(
        lambda request: httpx2.Response(
            200, content=html, headers={"Content-Type": "text/html"}
        )
    )
    target = tmp_path / "x.zip"
    with pytest.raises(CorruptPayloadError):
        client.download_resource("https://capes.test/x.zip", target, dataset_id="d")
    assert not target.exists()


def test_cliente_padrao_respeita_ambiente(monkeypatch: pytest.MonkeyPatch) -> None:
    """O cliente de catálogo vem do cliente padrão do host (``QUANTILICA_HTTP_*``)."""
    monkeypatch.setenv("QUANTILICA_HTTP_TIMEOUT", "12")
    monkeypatch.setenv("QUANTILICA_HTTP_ATTEMPTS", "2")
    client = CapesClient()
    assert client.client.timeout == 12.0
    assert client.client.attempts == 2


def test_cliente_padrao_da_descoberta_tem_ao_menos_300s(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("QUANTILICA_HTTP_TIMEOUT", raising=False)
    assert CapesClient().client.timeout >= 300.0


def _pkg(*resources: dict) -> dict:
    return {"name": "pacote-x", "resources": list(resources)}


def test_fusao_de_recursos_com_mesmo_nome_avisa(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Dois CSV de URLs diferentes com o mesmo nome: um é descartado, com aviso."""
    pkg = _pkg(
        {"name": "dados_2024", "format": "CSV", "url": "https://x/a.csv", "size": 5},
        {"name": "dados_2024", "format": "CSV", "url": "https://x/b.csv", "size": 9},
    )
    client = CapesClient()
    with caplog.at_level(logging.WARNING):
        picked = client.pick_package_resources(pkg)
    assert [r["url"] for r in picked] == ["https://x/b.csv"]  # escolha inalterada
    avisos = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(avisos) == 1
    msg = avisos[0].getMessage()
    assert "pacote-x" in msg
    assert "https://x/a.csv" in msg
    assert "https://x/b.csv" in msg


def test_csv_e_zip_com_mesmo_nome_avisa(caplog: pytest.LogCaptureFixture) -> None:
    pkg = _pkg(
        {"name": "dados", "format": "ZIP", "url": "https://x/a.zip"},
        {"name": "dados", "format": "CSV", "url": "https://x/a.csv"},
    )
    with caplog.at_level(logging.WARNING):
        picked = CapesClient().pick_package_resources(pkg)
    assert [r["format"] for r in picked] == ["CSV"]
    assert any(r.levelno == logging.WARNING for r in caplog.records)


def test_xlsx_duplicata_do_csv_nao_avisa(caplog: pytest.LogCaptureFixture) -> None:
    """O XLSX que duplica o CSV é a deduplicação esperada: sem WARNING."""
    pkg = _pkg(
        {"name": "dados_2024", "format": "XLSX", "url": "https://x/a.xlsx"},
        {"name": "dados_2024", "format": "CSV", "url": "https://x/a.csv"},
    )
    with caplog.at_level(logging.WARNING):
        CapesClient().pick_package_resources(pkg)
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]


def test_mesmo_nome_e_mesma_url_nao_avisa(caplog: pytest.LogCaptureFixture) -> None:
    pkg = _pkg(
        {"name": "dados", "format": "CSV", "url": "https://x/a.csv"},
        {"name": "dados", "format": "CSV", "url": "https://x/a.csv"},
    )
    with caplog.at_level(logging.WARNING):
        CapesClient().pick_package_resources(pkg)
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
