"""Catálogo completo da CAPES: 88 pacotes, 27 temas, tiers e aliases (sem rede)."""

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
    """O catálogo estático == package_list gravado em 2026-11-28 (88 pacotes)."""
    names = json.loads((FIXTURES / "package_list.json").read_text(encoding="utf-8"))
    assert len(names) == 88
    assert set(CATALOG) == set(names)


def test_27_temas_em_11_grupos() -> None:
    assert len({pkg.tema for pkg in CATALOG.values()}) == 27
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


def test_mudancas_de_2026_11_28() -> None:
    """Entram os dois pacotes novos; saem os três que a fonte deixou de publicar."""
    novos = {
        "2021-a-2025-servidores-da-capes": "gestao",
        "2023-a-2025-projetos-de-cooperacao-internacional-pesquisa-scba": "bolsas",
    }
    for slug, group in novos.items():
        assert CATALOG[slug].group == group
        assert CATALOG[slug].tier == "listed"
        assert CATALOG[slug].n_csv == (2 if group == "gestao" else 3)
    retirados = {
        "2021-a-2025-dotacao-e-execucao-orcamentaria-da-capes",
        "2023-a-2025-bolsas-dos-mestrados-profissionais-em-rede-nacional-proeb",
        "2023-a-2025-bolsistas-da-universidade-aberta-do-brasil-uab",
    }
    assert not retirados & set(CATALOG)


def test_pacote_listado_nunca_consulta_a_fonte(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Listado = só catálogo: a fonte tirar o pacote do ar não toca a coleta."""
    from capes_fetcher import catalog

    def boom(self: object, package_id: str) -> dict:
        raise AssertionError(f"package_show({package_id!r}) num grupo só listado")

    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(catalog.CapesClient, "package_show", boom)
    for group in ("pessoas", "producao", "projetos", "bolsas", "gestao", "fomento"):
        assert list_datasets(group) == []


def test_pacote_r1_ausente_na_fonte_e_erro_nao_lista_vazia(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pacote que baixa e some do CKAN levanta (o host conta o erro), não vira []."""
    from quantilica.core.exceptions import CkanError

    from capes_fetcher import catalog

    def gone(self: object, package_id: str) -> dict:
        raise CkanError("CKAN API error on package_show: Authorization Error")

    monkeypatch.setattr(catalog, "_CACHE", {})
    monkeypatch.setattr(catalog.CapesClient, "package_show", gone)
    for group in ("teses", "programas", "cursos"):
        with pytest.raises(CkanError):
            list_datasets(group)
