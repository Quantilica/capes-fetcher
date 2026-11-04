"""Catálogo CAPES do domínio ``fomento`` — Fomento, Dotação e Execução Orçamentária.

Gerado a partir do ``package_search`` do CKAN da CAPES (2026-11-03). ``tier="r1"``
baixa hoje; ``tier="listed"`` fica catalogado, com download em release futura.
Cada tema do portal é fatiado em pacotes por era (2004-2012, 2013-2016, ...).
"""

from __future__ import annotations

from ._catalog_base import CapesPackage

GROUP = "fomento"
NAME = "Fomento, Dotação e Execução Orçamentária"

PACKAGES: tuple[CapesPackage, ...] = (
    CapesPackage(
        slug="2012-a-2016-custeio-e-capital-dos-programas-de-fomento-da-diretoria-de-programas-e-bolsas-no-pais",
        group=GROUP,
        tema="custeio-dos-programas-de-fomento-da-diretoria-de-programas-e-bolsas-no-pais-dpb",
        title="Custeio e Capital dos Programas de Fomento PROAP e PROEX da Diretoria de Programas e Bolsas no País (DPB)",
        era_start=2012,
        era_end=2016,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2021-custeio-e-capital-dos-programas-de-fomento-da-diretoria-de-programas-e-bolsas-no-pais",
        group=GROUP,
        tema="custeio-dos-programas-de-fomento-da-diretoria-de-programas-e-bolsas-no-pais-dpb",
        title="Custeio e Capital dos Programas de Fomento PROAP e PROEX da Diretoria de Programas e Bolsas no País (DPB)",
        era_start=2017,
        era_end=2021,
        tier="listed",
        n_csv=1,
        n_xlsx=1,
        note="",
    ),
    CapesPackage(
        slug="2022-a-2025-custeio-e-capital-dos-programas-de-fomento-proap-e-proex-da-dpb",
        group=GROUP,
        tema="custeio-dos-programas-de-fomento-da-diretoria-de-programas-e-bolsas-no-pais-dpb",
        title="Custeio e Capital dos Programas de Fomento PROAP e PROEX da Diretoria de Programas e Bolsas no País (DPB)",
        era_start=2022,
        era_end=2025,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2013-a-2020-dotacao-e-execucao-orcamentaria-da-capes",
        group=GROUP,
        tema="dotacao-e-execucao-orcamentaria-da-capes",
        title="Dotação e Execução Orçamentária da Capes",
        era_start=2013,
        era_end=2020,
        tier="listed",
        n_csv=8,
        n_xlsx=8,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2025-dotacao-e-execucao-orcamentaria-da-capes",
        group=GROUP,
        tema="dotacao-e-execucao-orcamentaria-da-capes",
        title="Dotação e Execução Orçamentária da CAPES",
        era_start=2021,
        era_end=2025,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="bolsistas-da-universidade-aberta-do-brasil-uab-2013-a-2016",
        group=GROUP,
        tema="indicadores-de-bolsas-auxilios-e-projetos-da-ded-capes",
        title="Bolsistas da Universidade Aberta do Brasil (UAB)",
        era_start=2013,
        era_end=2016,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2017-a-2020-bolsistas-da-universidade-aberta-do-brasil-uab",
        group=GROUP,
        tema="indicadores-de-bolsas-auxilios-e-projetos-da-ded-capes",
        title="Bolsistas da Universidade Aberta do Brasil (UAB)",
        era_start=2017,
        era_end=2020,
        tier="listed",
        n_csv=4,
        n_xlsx=4,
        note="",
    ),
    CapesPackage(
        slug="2021-a-2022-bolsistas-da-universidade-aberta-do-brasil-uab",
        group=GROUP,
        tema="indicadores-de-bolsas-auxilios-e-projetos-da-ded-capes",
        title="Bolsistas da Universidade Aberta do Brasil (UAB)",
        era_start=2021,
        era_end=2022,
        tier="listed",
        n_csv=2,
        n_xlsx=2,
        note="",
    ),
    CapesPackage(
        slug="2023-a-2025-bolsistas-da-universidade-aberta-do-brasil-uab",
        group=GROUP,
        tema="indicadores-de-bolsas-auxilios-e-projetos-da-ded-capes",
        title="Bolsistas da Universidade Aberta do Brasil (UAB)",
        era_start=2023,
        era_end=2025,
        tier="listed",
        n_csv=2,
        n_xlsx=2,
        note="",
    ),
)
