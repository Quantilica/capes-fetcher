"""Dataset catalog for capes-fetcher."""

from __future__ import annotations

from typing import Any

from ._catalog_base import DatasetEntry, GroupInfo, annual_datasets
from .constants import CAPES_CKAN_URL, START_YEAR

__all__ = [
    "DatasetEntry",
    "GroupInfo",
    "GROUPS",
    "GROUP_ALIASES",
    "list_datasets",
]

_TESES_ENTRIES = [
    e.to_dict()
    for e in annual_datasets(
        "teses",
        base_id="teses",
        name_template="Catálogo de Teses e Dissertações {year}",
        url_template=f"{CAPES_CKAN_URL}/action/package_show?id=teses_{{year}}",
        start_year=START_YEAR,
        end_year=2024,
        ext="csv",
    )
]

_PROGRAMAS_ENTRIES = [
    e.to_dict()
    for e in annual_datasets(
        "programas",
        base_id="programas",
        name_template="Programas de Pós-Graduação Stricto Sensu {year}",
        url_template=f"{CAPES_CKAN_URL}/action/package_show?id=programas_{{year}}",
        start_year=2021,
        end_year=2024,
        ext="csv",
    )
]

_CURSOS_ENTRIES = [
    e.to_dict()
    for e in annual_datasets(
        "cursos",
        base_id="cursos",
        name_template="Cursos de Pós-Graduação Stricto Sensu {year}",
        url_template=f"{CAPES_CKAN_URL}/action/package_show?id=cursos_{{year}}",
        start_year=2021,
        end_year=2024,
        ext="csv",
    )
]

GROUPS: dict[str, dict[str, Any]] = {
    "teses": {
        "name": "Catálogo de Teses e Dissertações",
        "entries": _TESES_ENTRIES,
    },
    "programas": {
        "name": "Programas de Pós-Graduação Stricto Sensu",
        "entries": _PROGRAMAS_ENTRIES,
    },
    "cursos": {
        "name": "Cursos de Pós-Graduação Stricto Sensu",
        "entries": _CURSOS_ENTRIES,
    },
}

GROUP_ALIASES: dict[str, str] = {
    "padrao": "teses",
    "principal": "teses",
    "teses_dissertacoes": "teses",
    "teses-dissertacoes": "teses",
    "pos_graduacao": "programas",
    "pos-graduacao": "programas",
}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """List datasets for a group or all groups."""
    if group is None:
        entries: list[dict[str, Any]] = []
        for g_data in GROUPS.values():
            entries.extend(g_data["entries"])
        return entries

    canon = GROUP_ALIASES.get(group, group)
    if canon not in GROUPS:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    return list(GROUPS[canon]["entries"])
