"""Constants and endpoint definitions for capes-fetcher."""

from __future__ import annotations

CAPES_CKAN_URL = "https://dadosabertos.capes.gov.br"
CATALOGO_TESES_REST_URL = "https://catalogodeteses.capes.gov.br"

TESES_PACKAGES = [
    "1987-a-2012-catalogo-de-teses-e-dissertacoes-brasil",
    "catalogo-de-teses-e-dissertacoes-de-2013-a-2016",
    "2017-2020-catalogo-de-teses-e-dissertacoes-da-capes",
    "2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil",
]

PROGRAMAS_PACKAGES = [
    "programas-da-pos-graduacao-stricto-census-do-brasil-de-2013-a-2015",
    "2017-a-2020-programas-da-pos-graduacao-stricto-sensu-no-brasil",
    "2021-a-2024-programas-da-pos-graduacao-stricto-sensu-no-brasil",
]

CURSOS_PACKAGES = [
    "cursos-da-pos-graduacao-stricto-sensu-do-brasil-de-2013-a-2015",
    "2017-a-2020-cursos-da-pos-graduacao-stricto-sensu-no-brasil",
    "2021-a-2024-cursos-da-pos-graduacao-stricto-sensu-no-brasil",
]

START_YEAR = 1987
