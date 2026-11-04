"""Catálogo CAPES do domínio ``programas`` — Programas de Pós-Graduação Stricto Sensu.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "programas"
NAME = "Programas de Pós-Graduação Stricto Sensu"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="programas-da-pos-graduacao-stricto-census-do-brasil-de-2013-a-2015",
        group=GROUP,
        tema="programas-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Programas da Pós-Graduação Stricto Sensu do Brasil",
        era_start=2013,
        era_end=2016,
        tier="r1",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-programas-da-pos-graduacao-stricto-sensu-no-brasil",
        group=GROUP,
        tema="programas-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Programas da Pós-Graduação Stricto Sensu no Brasil",
        era_start=2017,
        era_end=2020,
        tier="r1",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2024-programas-da-pos-graduacao-stricto-sensu-no-brasil",
        group=GROUP,
        tema="programas-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Programas da Pós-Graduação Stricto Sensu no Brasil",
        era_start=2021,
        era_end=2024,
        tier="r1",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
)
