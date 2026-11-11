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


def _clear_http_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "QUANTILICA_HTTP_TIMEOUT",
        "QUANTILICA_HTTP_ATTEMPTS",
        "QUANTILICA_HTTP_RETRY_DELAY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_download_client_aguenta_arquivo_de_450mb_a_baixa_vazao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Teses de ~450 MB a ~0,4 MB/s (~20 min), sem ``Range`` (sem retomada).

    O timeout do httpx é de leitura (tempo sem receber bytes), e o core não
    impõe teto total ao download. As tentativas são poucas porque cada uma
    perdida pode custar dezenas de minutos e o cron tem ``CRON_TIMEOUT``.
    """
    from capes_fetcher import plugin

    _clear_http_env(monkeypatch)
    client = plugin._build_client()
    assert client.timeout >= 400  # cobre o 504 do proxy (~300 s) e pausas no corpo
    assert 2 <= client.attempts <= 6
    assert client.retry_base_delay >= 10  # compensa as poucas tentativas no 503
    # Pior caso de falhas lentas cabe no CRON_TIMEOUT=14400 do cron da CAPES,
    # com folga para o outro arquivo grande: tentativas * (20 min + leitura).
    assert client.attempts * (1200 + client.timeout) <= 14400
    assert client._build_client().timeout.read == client.timeout
    # Sem gzip o servidor sempre informa o tamanho do CSV (verificável).
    assert client.headers["Accept-Encoding"] == "identity"


def test_download_client_respeita_o_ambiente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from capes_fetcher import plugin

    monkeypatch.setenv("QUANTILICA_HTTP_TIMEOUT", "42")
    monkeypatch.setenv("QUANTILICA_HTTP_ATTEMPTS", "7")
    monkeypatch.setenv("QUANTILICA_HTTP_RETRY_DELAY", "3")
    client = plugin._build_client()
    assert client.timeout == 42.0
    assert client.attempts == 7
    assert client.retry_base_delay == 3.0
