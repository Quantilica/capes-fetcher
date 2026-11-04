"""Catálogo CAPES do domínio ``teses`` — Catálogo de Teses e Dissertações.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "teses"
NAME = "Catálogo de Teses e Dissertações"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="1987-a-2012-catalogo-de-teses-e-dissertacoes-brasil",
        group=GROUP,
        tema="catalogo-de-teses-e-dissertacoes-brasil",
        title="Catálogo de Teses e Dissertações - Brasil",
        era_start=1987,
        era_end=2012,
        tier="r1",
        n_csv=26,
        n_xlsx=26,
        note="",
    ),
    CapesPackage(
        slug="catalogo-de-teses-e-dissertacoes-de-2013-a-2016",
        group=GROUP,
        tema="catalogo-de-teses-e-dissertacoes-brasil",
        title="Catálogo de Teses e Dissertações - Brasil",
        era_start=2013,
        era_end=2016,
        tier="r1",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2017-2020-catalogo-de-teses-e-dissertacoes-da-capes",
        group=GROUP,
        tema="catalogo-de-teses-e-dissertacoes-brasil",
        title="Catálogo de Teses e Dissertações - Brasil",
        era_start=2017,
        era_end=2020,
        tier="r1",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil",
        group=GROUP,
        tema="catalogo-de-teses-e-dissertacoes-brasil",
        title="Catálogo de Teses e Dissertações - Brasil",
        era_start=2021,
        era_end=2024,
        tier="r1",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
)
