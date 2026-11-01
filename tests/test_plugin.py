"""Tests for capes-fetcher Typer plugin."""

from typer.testing import CliRunner

from capes_fetcher.plugin import app


def test_cli_list() -> None:
    """Test quantilica capes list."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "teses" in result.output


def test_cli_convert_help() -> None:
    """Test quantilica capes convert --help."""
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "--lake" in result.output
