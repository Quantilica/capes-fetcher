"""Dataset catalog for capes-fetcher.

Os pacotes do CKAN da CAPES não têm um recurso por ano: cada pacote cobre um
período (ex.: 2021–2024) e publica um CSV por ano dentro dele. O catálogo é
portanto **descoberto** a partir de ``package_show`` — essa é a única forma de
conhecer a URL real do recurso e o ano a que ele se refere.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from .client import CapesClient
from .constants import CURSOS_PACKAGES, PROGRAMAS_PACKAGES, TESES_PACKAGES

__all__ = [
    "GROUPS",
    "GROUP_ALIASES",
    "list_datasets",
]

_CACHE: dict[str, list[dict[str, Any]]] = {}

_YEAR_RE = re.compile(r"(19|20)\d{2}")
_FORMATOS = {"CSV", "ZIP"}


def _slugify(value: str) -> str:
    """Normaliza um nome de recurso para usar como id/partição."""
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^\w-]+", "-", normalized).strip("-").lower()


def _resource_year(name: str, url: str) -> int | None:
    """Extrai o ano do nome do recurso (fallback: da URL)."""
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
            if ident in seen:
                ident = f"{ident}_{_slugify(package_slug)[:12]}"
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
                    "slug": None,
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
    else:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    _CACHE[group] = entries
    return entries


GROUPS: dict[str, dict[str, Any]] = {
    "teses": {
        "name": "Catálogo de Teses e Dissertações",
        "entries": [],
    },
    "programas": {
        "name": "Programas de Pós-Graduação Stricto Sensu",
        "entries": [],
    },
    "cursos": {
        "name": "Cursos de Pós-Graduação Stricto Sensu",
        "entries": [],
    },
}

GROUP_ALIASES: dict[str, str] = {
    "padrao": "teses",
    "principal": "teses",
    "teses_dissertacoes": "teses",
    "teses-dissertacoes": "teses",
    "pos_graduacao": "programas",
    "pos-graduacao": "programas",
}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Lista recursos reais dos pacotes CKAN, por grupo."""
    if group is None:
        entries: list[dict[str, Any]] = []
        for group_id in GROUPS:
            entries.extend(_group_entries(group_id))
        return entries

    canon = GROUP_ALIASES.get(group, group)
    if canon not in GROUPS:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    return list(_group_entries(canon))
