"""Testes do ``discover`` da CAPES com package_list/package_search gravados."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from capes_fetcher.discover import discover

FIXTURES = Path(__file__).parent / "fixtures"


def _names() -> list[str]:
    return json.loads((FIXTURES / "package_list.json").read_text(encoding="utf-8"))


def test_package_list_atual_nao_tem_novidade() -> None:
    report = discover(_names())
    assert report.known == 89
    assert not report.has_changes


def test_detecta_era_nova_e_pacote_removido() -> None:
    names = _names()
    names.remove("2017-a-2020-servidores-da-capes")
    names.append("2025-a-2028-catalogo-de-teses-e-dissertacoes-brasil")
    report = discover(names)
    assert [p["slug"] for p in report.new_packages] == [
        "2025-a-2028-catalogo-de-teses-e-dissertacoes-brasil"
    ]
    assert report.removed_packages == ["2017-a-2020-servidores-da-capes"]


def test_package_search_amostra_sem_crescimento() -> None:
    packages = json.loads(
        (FIXTURES / "package_search_amostra.json").read_text(encoding="utf-8")
    )["packages"]
    report = discover(packages)
    assert report.new_packages == []
    assert report.known == 3
    assert report.grown_packages == {}


def test_resposta_vazia_vira_erro() -> None:
    with pytest.raises(RuntimeError, match="não devolveu pacotes"):
        discover([])
