"""Catálogo CAPES do domínio ``formacao-professores`` — Formação de Professores da Educação Básica.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "formacao-professores"
NAME = "Formação de Professores da Educação Básica"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="2009-a-2012-bolsas-para-a-formacao-de-professores-da-educacao-basica",
        group=GROUP,
        tema="bolsas-para-a-formacao-de-professores-da-educacao-basica",
        title="Bolsas para a Formação de Professores da Educação Básica",
        era_start=2009,
        era_end=2012,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="bolsas-para-a-formacao-de-professores-da-educacao-basica-2013-a-2016",
        group=GROUP,
        tema="bolsas-para-a-formacao-de-professores-da-educacao-basica",
        title="Bolsas para a Formação de Professores da Educação Básica",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=6,
        n_xlsx=6,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-bolsas-para-a-formacao-de-professores-da-educacao-basica",
        group=GROUP,
        tema="bolsas-para-a-formacao-de-professores-da-educacao-basica",
        title="Bolsas para a Formação de Professores da Educação Básica",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=5,
        n_xlsx=5,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2022-bolsas-para-a-formacao-de-professores-da-educacao-basica",
        group=GROUP,
        tema="bolsas-para-a-formacao-de-professores-da-educacao-basica",
        title="Bolsas para a Formação de Professores da Educação Básica",
        era_start=2021,
        era_end=2022,
        tier="listed",
        n_csv=2,
        n_xlsx=2,
        note="",
    ),
    CapesPackage(
        slug="2023-a-2025-bolsas-para-a-formacao-de-professores-da-educacao-basica",
        group=GROUP,
        tema="bolsas-para-a-formacao-de-professores-da-educacao-basica",
        title="Bolsas para a Formação de Professores da Educação Básica",
        era_start=2023,
        era_end=2025,
        tier="listed",
        n_csv=3,
        n_xlsx=5,
        note="",
    ),
    CapesPackage(
        slug="2013-a-2025-participantes-de-programas-de-formacao-de-professores-da-educacao-basica-no-exterior",
        group=GROUP,
        tema="participantes-de-programas-de-formacao-de-professores-da-educacao-basica-no-exterior",
        title="Participantes de Programas de Formação de Professores da Educação Básica no Exterior",
        era_start=2013,
        era_end=2025,
        tier="listed",
        n_csv=2,
        n_xlsx=2,
        note="",
    ),
    CapesPackage(
        slug="2018-a-2025-projetos-de-formacao-inicial-de-professores-da-educacao-basica",
        group=GROUP,
        tema="projetos-de-formacao-inicial-de-professores-da-educacao-basica",
        title="Projetos de Formação Inicial de Professores da Educação Básica",
        era_start=2018,
        era_end=2025,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="2014-a-2025-recursos-investidos-para-formacao-de-professores-da-educacao-basica",
        group=GROUP,
        tema="recursos-investidos-para-formacao-de-professores-da-educacao-basica",
        title="Recursos investidos para Formação de Professores da Educação Básica",
        era_start=2014,
        era_end=2025,
        tier="listed",
        n_csv=2,
        n_xlsx=2,
        note="",
    ),
)
