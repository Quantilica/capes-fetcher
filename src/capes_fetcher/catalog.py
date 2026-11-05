"""Dataset catalog for capes-fetcher.

Os pacotes do CKAN da CAPES não têm um recurso por ano: cada pacote cobre um
período (ex.: 2021–2024) e publica um CSV por ano dentro dele. O catálogo é
portanto **descoberto** a partir de ``package_show`` — essa é a única forma de
conhecer a URL real do recurso e o ano a que ele se refere.

O catálogo é em duas camadas, com um módulo ``catalog_<dominio>.py`` por grupo
(``CATALOG`` traz os 89 pacotes do CKAN, fatias por era dos 26 temas do portal):

- ``tier="r1"``: baixa hoje (teses, programas e cursos); é o que
  :func:`list_datasets` expande;
- ``tier="listed"``: catalogado, com download em release futura; visível em
  :func:`catalog_rows` e no comando ``catalogo``.

O catálogo web de teses (``catalogodeteses.capes.gov.br``) só aceita POST com
20 registros por página e não serve para coleta em massa: fica fora.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from . import (
    catalog_bolsas,
    catalog_cursos,
    catalog_fomento,
    catalog_formacao_professores,
    catalog_gestao,
    catalog_periodicos,
    catalog_pessoas,
    catalog_producao,
    catalog_programas,
    catalog_projetos,
    catalog_teses,
)
from ._catalog_base import CapesPackage
from .client import CapesClient
from .constants import CURSOS_PACKAGES, PROGRAMAS_PACKAGES, TESES_PACKAGES

__all__ = [
    "GROUPS",
    "GROUP_ALIASES",
    "MACRO_ALIASES",
    "CATALOG",
    "CapesPackage",
    "catalog_rows",
    "expand_group",
    "list_datasets",
]

_MODULES = [
    catalog_teses,
    catalog_programas,
    catalog_cursos,
    catalog_pessoas,
    catalog_producao,
    catalog_projetos,
    catalog_bolsas,
    catalog_formacao_professores,
    catalog_fomento,
    catalog_periodicos,
    catalog_gestao,
]

# slug do pacote -> descritor, de todos os pacotes catalogados (R1 e listados).
CATALOG: dict[str, CapesPackage] = {
    pkg.slug: pkg for mod in _MODULES for pkg in mod.PACKAGES
}

_CACHE: dict[str, list[dict[str, Any]]] = {}

_YEAR_RE = re.compile(r"(19|20)\d{2}")
# Pacotes multianuais (ex.: "...-2013A2016-2020-06-12_2014") trazem o ano do
# recurso depois do último "_"; o primeiro ano do nome é o início da era.
_TRAILING_YEAR_RE = re.compile(r"_((?:19|20)\d{2})$")
_FORMATOS = {"CSV", "ZIP"}


def _slugify(value: str) -> str:
    """Normaliza um nome de recurso para usar como id/partição."""
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^\w-]+", "-", normalized).strip("-").lower()


def _resource_year(name: str, url: str) -> int | None:
    """Extrai o ano do nome do recurso (fallback: da URL).

    Um sufixo ``_AAAA`` no fim do nome ou do arquivo tem precedência sobre o
    primeiro ano encontrado (que, nos pacotes de várias eras, é o da era).
    """
    stem = url.rsplit("/", 1)[-1].split("?", 1)[0].rsplit(".", 1)[0]
    trailing = _TRAILING_YEAR_RE.search(name) or _TRAILING_YEAR_RE.search(stem)
    if trailing:
        return int(trailing.group(1))
    match = _YEAR_RE.search(name) or _YEAR_RE.search(url.rsplit("/", 1)[-1])
    return int(match.group(0)) if match else None


def _resource_ext(url: str, fmt: str) -> str:
    """Extensão real do arquivo a partir da URL (fallback: formato CKAN)."""
    filename = url.rsplit("/", 1)[-1].split("?", 1)[0]
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return fmt.lower()


def _entries_for_group(
    group: str, base_id: str, packages: list[str]
) -> list[dict[str, Any]]:
    """Expande os pacotes CKAN em uma entrada por recurso CSV/ZIP."""
    client = CapesClient()
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for package_slug in packages:
        package = client.package_show(package_slug)
        for resource in client.pick_package_resources(package):
            fmt = str(resource.get("format") or "").strip().upper()
            if fmt not in _FORMATOS:
                continue
            url = str(resource.get("url") or "")
            if not url:
                continue
            name = str(resource.get("name") or resource.get("id") or package_slug)
            year = _resource_year(name, url)
            ident = f"{base_id}_{year}" if year else f"{base_id}_{_slugify(name)}"
            slug: str | None = None
            if ident in seen:
                # Mantém o sufixo histórico (pacote) e, se ainda colidir,
                # acrescenta o id curto do recurso (estável no CKAN).
                slug = _slugify(package_slug)[:12]
                if f"{ident}_{slug}" in seen:
                    slug = f"{slug}_{_slugify(str(resource.get('id') or name))[:8]}"
                ident = f"{ident}_{slug}"
                n = 1
                while ident in seen:  # último recurso: contador
                    n += 1
                    ident = f"{ident}_{n}"
            seen.add(ident)
            entries.append(
                {
                    "id": ident,
                    "base_id": base_id,
                    "name": name,
                    "url": url,
                    "ext": _resource_ext(url, fmt),
                    "group": group,
                    "year": year,
                    "slug": slug,
                    "remote_size": resource.get("size"),
                    "remote_modified": resource.get("last_modified"),
                }
            )
    return entries


def _group_entries(group: str) -> list[dict[str, Any]]:
    """Entries do grupo, com cache por processo."""
    if group in _CACHE:
        return _CACHE[group]
    if group == "teses":
        entries = _entries_for_group("teses", "teses", TESES_PACKAGES)
    elif group == "programas":
        entries = _entries_for_group("programas", "programas", PROGRAMAS_PACKAGES)
    elif group == "cursos":
        entries = _entries_for_group("cursos", "cursos", CURSOS_PACKAGES)
    elif group in GROUPS:
        entries = []  # só pacotes listados (download em release futura)
    else:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    _CACHE[group] = entries
    return entries


GROUPS: dict[str, dict[str, Any]] = {
    mod.GROUP: {"name": mod.NAME, "entries": []} for mod in _MODULES
}

# Macro-aliases: um apelido que engloba vários grupos canônicos.
MACRO_ALIASES: dict[str, list[str]] = {
    "pos-graduacao": [
        "teses",
        "programas",
        "cursos",
        "pessoas",
        "producao",
        "projetos",
    ],
    "bolsas-e-fomento": ["bolsas", "formacao-professores", "fomento"],
    "institucional": ["periodicos", "gestao"],
}

GROUP_ALIASES: dict[str, list[str]] = {
    **MACRO_ALIASES,
    "padrao": ["teses"],
    "principal": ["teses"],
    "teses_dissertacoes": ["teses"],
    "teses-dissertacoes": ["teses"],
    "pos_graduacao": ["programas"],
    "docentes": ["pessoas"],
    "discentes": ["pessoas"],
    "producao-intelectual": ["producao"],
    "capes": ["gestao"],
}


def expand_group(key: str) -> list[str]:
    """Expande um grupo, alias ou macro-alias em ids canônicos de grupo.

    Raises:
        ValueError: Se ``key`` não for grupo nem alias.
    """
    if key in GROUPS:
        return [key]
    targets = GROUP_ALIASES.get(key)
    if targets is None:
        raise ValueError(f"Grupo desconhecido: {key!r}")
    return [t for t in targets if t in GROUPS]


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Lista recursos reais dos pacotes CKAN R1 (teses, programas, cursos).

    Só o tier ``r1`` baixa hoje; os demais pacotes aparecem em
    :func:`catalog_rows`.
    """
    groups = list(GROUPS) if group is None else expand_group(group)
    entries: list[dict[str, Any]] = []
    for group_id in groups:
        entries.extend(_group_entries(group_id))
    return entries


def catalog_rows(
    group: str | None = None, tier: str | None = None
) -> list[dict[str, Any]]:
    """Linhas do catálogo estático (um pacote por linha), sem rede."""
    groups = set(GROUPS if group is None else expand_group(group))
    return [
        pkg.to_dict()
        for pkg in CATALOG.values()
        if pkg.group in groups and (tier is None or pkg.tier == tier)
    ]
