"""Catálogo completo da CAPES: 89 pacotes, 26 temas, tiers e aliases (sem rede)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from capes_fetcher.catalog import (
    CATALOG,
    GROUP_ALIASES,
    GROUPS,
    MACRO_ALIASES,
    catalog_rows,
    expand_group,
    list_datasets,
)
from capes_fetcher.constants import (
    CURSOS_PACKAGES,
    PROGRAMAS_PACKAGES,
    TESES_PACKAGES,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_catalogo_cobre_todos_os_pacotes_do_package_list() -> None:
    """O catálogo estático == package_list gravado em 2026-11-03 (89 pacotes)."""
    names = json.loads((FIXTURES / "package_list.json").read_text(encoding="utf-8"))
    assert len(names) == 89
    assert set(CATALOG) == set(names)


def test_26_temas_em_11_grupos() -> None:
    assert len({pkg.tema for pkg in CATALOG.values()}) == 26
    assert len(GROUPS) == 11
    for group in GROUPS:
        assert catalog_rows(group), group


def test_tier_r1_e_o_das_constantes() -> None:
    r1 = {r["slug"] for r in catalog_rows(tier="r1")}
    assert r1 == set(TESES_PACKAGES + PROGRAMAS_PACKAGES + CURSOS_PACKAGES)
    assert len(r1) == 10
    assert CATALOG[TESES_PACKAGES[0]].group == "teses"


def test_grupos_so_listados_nao_baixam(monkeypatch: pytest.MonkeyPatch) -> None:
    """Grupos sem R1 devolvem lista vazia no list (sem tocar a rede)."""
    for group in ("pessoas", "bolsas", "gestao", "periodicos"):
        assert list_datasets(group) == []


def test_aliases_e_macro_aliases() -> None:
    for alias in GROUP_ALIASES:
        assert set(expand_group(alias)) <= set(GROUPS)
    assert set(MACRO_ALIASES) <= set(GROUP_ALIASES)
    assert expand_group("docentes") == ["pessoas"]
    assert "teses" in expand_group("pos-graduacao")
    with pytest.raises(ValueError, match="Grupo desconhecido"):
        expand_group("nada")


def test_eras_validas() -> None:
    for pkg in CATALOG.values():
        assert 1987 <= pkg.era_start <= pkg.era_end <= 2026
