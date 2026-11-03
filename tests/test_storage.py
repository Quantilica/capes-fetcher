"""Tests for capes-fetcher storage layer."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from capes_fetcher.storage import DataRepository


def test_path_for_entry_with_timestamp() -> None:
    """When last_modified is provided, filename uses that date."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {"group": "teses", "base_id": "btd", "ext": "csv", "year": 2023}

    path = repo.path_for_entry(entry, last_modified=dt.date(2023, 3, 31))

    assert "btd_2023@20230331.csv" in str(path)


def test_path_for_entry_fallback_timestamp() -> None:
    """When last_modified is None, filename gets today's @YYYYMMDD timestamp."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {"group": "teses", "base_id": "btd", "ext": "csv", "year": 2023}

    path = repo.path_for_entry(entry, last_modified=None)

    today = dt.date.today()
    expected_stamp = f"@{today:%Y%m%d}.csv"
    assert expected_stamp in str(path)


def test_path_for_entry_no_year_uses_timestamp() -> None:
    """When year is None, stamp_filename is used with fallback timestamp."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {"group": "teses", "base_id": "btd", "ext": "csv"}

    path = repo.path_for_entry(entry, last_modified=None)

    today = dt.date.today()
    expected_stamp = f"btd@{today:%Y%m%d}.csv"
    assert expected_stamp in str(path)


def test_path_for_entry_quarter_uses_timestamp() -> None:
    """Quarter partition uses fallback timestamp when last_modified is None."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {
        "group": "teses",
        "base_id": "btd",
        "ext": "csv",
        "year": 2023,
        "quarter": 1,
    }

    path = repo.path_for_entry(entry, last_modified=None)

    today = dt.date.today()
    expected_stamp = f"btd_2023-T01@{today:%Y%m%d}.csv"
    assert expected_stamp in str(path)


def test_path_for_entry_month_uses_timestamp() -> None:
    """Month partition uses fallback timestamp when last_modified is None."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {"group": "teses", "base_id": "btd", "ext": "csv", "year": 2023, "month": 3}

    path = repo.path_for_entry(entry, last_modified=None)

    today = dt.date.today()
    expected_stamp = f"btd_2023-03@{today:%Y%m%d}.csv"
    assert expected_stamp in str(path)
