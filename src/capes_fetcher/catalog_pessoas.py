"""Catálogo CAPES do domínio ``pessoas`` — Docentes e Discentes da Pós-Graduação.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "pessoas"
NAME = "Docentes e Discentes da Pós-Graduação"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="discentes-dos-programas-de-pos-graduacao-stricto-sensu-no-brasil-2004-a-2012",
        group=GROUP,
        tema="discentes-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Discentes dos Programas de Pós-Graduação stricto sensu no Brasil",
        era_start=2004,
        era_end=2012,
        tier="listed",
        n_csv=9,
        n_xlsx=9,
        note="",
    ),
    CapesPackage(
        slug="discentes-da-pos-graduacao-stricto-sensu-do-brasil-2013-a-2016",
        group=GROUP,
        tema="discentes-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Discentes da Pós-Graduação Stricto Sensu do Brasil",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="discentes-da-pos-graduacao-stricto-sensu-do-brasil-2017-a-2019",
        group=GROUP,
        tema="discentes-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Discentes da Pós-Graduação stricto sensu do Brasil",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2024-discentes-da-pos-graduacao-stricto-sensu-do-brasil",
        group=GROUP,
        tema="discentes-da-pos-graduacao-stricto-sensu-do-brasil",
        title="Discentes da Pós-Graduação Stricto Sensu no Brasil",
        era_start=2021,
        era_end=2024,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="coleta-de-dados-docentes-dos-programas-de-pos-graduacao-stricto-sensu-no-brasil-2004-a-2012",
        group=GROUP,
        tema="docentes-da-pos-graduacao-stricto-sensu-no-brasil",
        title="Docentes dos Programas de Pós-Graduação stricto sensu no Brasil",
        era_start=2004,
        era_end=2012,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="docentes-da-pos-graduacao-stricto-sensu-do-brasil-2013-a-2016",
        group=GROUP,
        tema="docentes-da-pos-graduacao-stricto-sensu-no-brasil",
        title="Docentes da Pós-Graduação Stricto Sensu no Brasil",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-docentes-da-pos-graduacao-stricto-sensu-no-brasil",
        group=GROUP,
        tema="docentes-da-pos-graduacao-stricto-sensu-no-brasil",
        title="Docentes da Pós-Graduação Stricto Sensu no Brasil",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2024-docentes-da-pos-graduacao-stricto-sensu-no-brasil",
        group=GROUP,
        tema="docentes-da-pos-graduacao-stricto-sensu-no-brasil",
        title="Docentes da Pós-Graduação Stricto Sensu no Brasil",
        era_start=2021,
        era_end=2024,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
)
