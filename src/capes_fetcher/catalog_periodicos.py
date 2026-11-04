"""Catálogo CAPES do domínio ``periodicos`` — Acessos ao Portal de Periódicos.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "periodicos"
NAME = "Acessos ao Portal de Periódicos"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="2010-a-2012-acessos-ao-portal-de-periodicos",
        group=GROUP,
        tema="acessos-ao-portal-de-periodicos-da-capes",
        title="Acessos ao Portal de Periódicos",
        era_start=2010,
        era_end=2012,
        tier="listed",
        n_csv=3,
        n_xlsx=3,
        note="",
    ),
    CapesPackage(
        slug="acesso-ao-portal-de-periodicos-2013-a-2016",
        group=GROUP,
        tema="acessos-ao-portal-de-periodicos-da-capes",
        title="Acessos ao Portal de Periódicos",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-acessos-ao-portal-de-periodicos",
        group=GROUP,
        tema="acessos-ao-portal-de-periodicos-da-capes",
        title="Acessos ao Portal de Periódicos",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2022-acessos-ao-portal-de-periodicos",
        group=GROUP,
        tema="acessos-ao-portal-de-periodicos-da-capes",
        title="Acessos ao Portal de Periódicos",
        era_start=2021,
        era_end=2022,
        tier="listed",
        n_csv=2,
        n_xlsx=2,
        note="",
    ),
    CapesPackage(
        slug="2023-a-2025-acessos-ao-portal-de-periodicos",
        group=GROUP,
        tema="acessos-ao-portal-de-periodicos-da-capes",
        title="Acessos ao Portal de Periódicos",
        era_start=2023,
        era_end=2025,
        tier="listed",
        n_csv=3,
        n_xlsx=3,
        note="",
    ),
)
