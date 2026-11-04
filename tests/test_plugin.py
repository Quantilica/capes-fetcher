"""Tests for capes-fetcher Typer plugin (offline por padrão)."""

import re
from typing import Any

import pytest
from typer.testing import CliRunner

from capes_fetcher import catalog
from capes_fetcher.plugin import app


@pytest.fixture
def offline_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Catálogo CKAN falso: nenhum teste padrão toca a rede."""

    def fake_group_entries(group: str) -> list[dict[str, Any]]:
        return [
            {
                "id": f"{group}_2023",
                "base_id": group,
                "name": f"{group} 2023",
                "url": f"https://example.invalid/{group}_2023.csv",
                "ext": "csv",
                "group": group,
                "year": 2023,
                "slug": None,
                "remote_size": 1,
                "remote_modified": None,
            }
        ]

    monkeypatch.setattr(catalog, "_group_entries", fake_group_entries)


def test_cli_list(offline_catalog: None) -> None:
    """Test quantilica capes list (catálogo mockado, sem rede)."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "teses" in result.output


@pytest.mark.network
def test_cli_list_live() -> None:
    """Contra o CKAN real da CAPES; só roda com ``pytest -m network``."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "teses" in result.output


def test_cli_convert_help() -> None:
    """Test quantilica capes convert --help."""
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "--lake" in re.sub(r"\x1b\[[0-9;]*m", "", result.output)


def test_aliases_resolve_to_group_not_characters() -> None:
    """Regressão: alias string virava lista de caracteres no FetcherApp."""
    from capes_fetcher.catalog import GROUP_ALIASES, GROUPS
    from capes_fetcher.plugin import fetcher

    for alias, canon in GROUP_ALIASES.items():
        assert fetcher.resolve_groups([alias]) == canon
        assert all(group in GROUPS for group in canon)
