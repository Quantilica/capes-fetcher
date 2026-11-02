"""Tests for capes-fetcher catalog (sem rede)."""

from __future__ import annotations

import pytest

from capes_fetcher import catalog
from capes_fetcher.catalog import GROUP_ALIASES, GROUPS, list_datasets

FAKE_RESOURCES = {
    "pkg-a": [
        {
            "name": "BR-CAPES-BTD-2023-2025-03-31",
            "format": "CSV",
            "url": "https://x/dataset/abc/resource/1/download/br-capes-btd-2023.csv",
            "size": 10,
            "last_modified": "2025-03-31",
        },
        {
            "name": "Metadados",
            "format": "PDF",
            "url": "https://x/metadados.pdf",
        },
    ],
    "pkg-b": [
        {
            "name": "BR-CAPES-BTD-2022-2025-03-31",
            "format": "CSV",
            "url": "https://x/dataset/def/resource/2/download/br-capes-btd-2022.csv",
            "size": 20,
        },
    ],
}


@pytest.fixture(autouse=True)
def fake_ckan(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a descoberta CKAN por um pacote fixo e limpa o cache."""
    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(
        catalog, "TESES_PACKAGES", ["pkg-a", "pkg-b"], raising=False
    )
    monkeypatch.setattr(catalog, "PROGRAMAS_PACKAGES", ["pkg-a"], raising=False)
    monkeypatch.setattr(catalog, "CURSOS_PACKAGES", ["pkg-b"], raising=False)
    monkeypatch.setattr(
        catalog.CapesClient,
        "package_show",
        lambda self, package_id: {"resources": FAKE_RESOURCES[package_id]},
    )
    monkeypatch.setattr(
        catalog.CapesClient,
        "pick_package_resources",
        lambda self, package, prefer=("CSV", "ZIP"): package["resources"],
    )


def test_expande_recursos_csv_e_ignora_pdf() -> None:
    """Um CSV por recurso, com ano e URL reais; PDF fica de fora."""
    entries = list_datasets("teses")
    assert [e["id"] for e in entries] == ["teses_2023", "teses_2022"]
    assert entries[0]["url"].endswith(".csv")
    assert entries[0]["ext"] == "csv"
    assert entries[0]["group"] == "teses"
    assert entries[0]["year"] == 2023


def test_list_datasets_por_grupo_e_alias() -> None:
    """Grupos e aliases válidos respondem; inválido levanta ValueError."""
    for group in GROUPS:
        assert isinstance(list_datasets(group), list)
    for alias in GROUP_ALIASES:
        assert isinstance(list_datasets(alias), list)
    with pytest.raises(ValueError, match="Grupo desconhecido"):
        list_datasets("grupo_inexistente_xyz")
