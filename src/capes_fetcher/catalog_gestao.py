"""Catálogo CAPES do domínio ``gestao`` — Gestão: Contratos e Servidores da CAPES.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "gestao"
NAME = "Gestão: Contratos e Servidores da CAPES"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="dados-relacionados-a-contratos-realizados-pela-capes-2013-a-2016",
        group=GROUP,
        tema="contratos-realizados-pela-capes",
        title="Contratos realizados pela CAPES",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-contratos-realizados-pela-capes",
        group=GROUP,
        tema="contratos-realizados-pela-capes",
        title="Contratos realizados pela CAPES",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2022-contratos-realizados-pela-capes",
        group=GROUP,
        tema="contratos-realizados-pela-capes",
        title="Contratos realizados pela CAPES",
        era_start=2021,
        era_end=2022,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="dados-de-servidores-da-capes-2013-a-2016",
        group=GROUP,
        tema="servidores-da-capes",
        title="Servidores da Capes",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-servidores-da-capes",
        group=GROUP,
        tema="servidores-da-capes",
        title="Servidores da Capes",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
)
