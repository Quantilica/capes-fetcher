"""Shared types and helper constructors for capes-fetcher catalogs."""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass
from typing import Any, Literal

Tier = Literal["r1", "listed"]


@dataclass(frozen=True)
class DatasetEntry:
    """Represents a single dataset entry to be downloaded."""

    id: str
    base_id: str
    name: str
    url: str
    ext: str
    group: str
    source: str = "capes"
    year: int | None = None
    quarter: int | None = None
    month: int | None = None
    slug: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dict."""
        return asdict(self)


@dataclass(frozen=True)
class GroupInfo:
    """Represents a logical group of dataset entries."""

    name: str
    entries: list[DatasetEntry]

    def to_dict(self) -> dict[str, Any]:
        """Convert group to dict."""
        return {
            "name": self.name,
            "entries": [e.to_dict() for e in self.entries],
        }


def static_dataset(
    group: str,
    *,
    id: str,
    name: str,
    url: str,
    ext: str = "csv",
) -> DatasetEntry:
    """Construct a static (single-file) dataset entry."""
    return DatasetEntry(
        id=id,
        base_id=id,
        name=name,
        url=url,
        ext=ext,
        group=group,
    )


def annual_datasets(
    group: str,
    *,
    base_id: str,
    name_template: str,
    url_template: str,
    start_year: int,
    end_year: int | None = None,
    ext: str = "csv",
) -> list[DatasetEntry]:
    """Construct annual dataset entries."""
    end = end_year or dt.date.today().year
    return [
        DatasetEntry(
            id=f"{base_id}_{y}",
            base_id=base_id,
            name=name_template.format(year=y),
            url=url_template.format(year=y),
            ext=ext,
            group=group,
            year=y,
        )
        for y in range(start_year, end + 1)
    ]


@dataclass(frozen=True)
class CapesPackage:
    """Descritor estático de um pacote do CKAN da CAPES.

    Cada tema do portal é fatiado em 2 a 6 pacotes por era; ``tema`` é o grupo
    CKAN específico do pacote (os 26 temas do portal).

    Attributes:
        slug: Nome do pacote no CKAN.
        group: Grupo (domínio) canônico do catálogo.
        tema: Grupo CKAN específico (tema) do pacote.
        title: Título do pacote, sem o prefixo de era.
        era_start: Primeiro ano coberto pelo pacote.
        era_end: Último ano coberto pelo pacote.
        tier: ``r1`` (baixa hoje) ou ``listed`` (listado; download em release futura).
        n_csv: Recursos CSV no snapshot de 2026-11-03.
        n_xlsx: Recursos XLSX (duplicam os CSV; nunca baixados).
        note: Observação.
    """

    slug: str
    group: str
    tema: str
    title: str
    era_start: int
    era_end: int
    tier: Tier
    n_csv: int = 0
    n_xlsx: int = 0
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Converte o descritor em dict."""
        return asdict(self)
