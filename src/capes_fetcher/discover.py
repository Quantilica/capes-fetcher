"""Descoberta de pacotes novos e removidos da CAPES frente ao catálogo estático.

Compara o ``package_list`` (ou o ``package_search``, se já estiver em mãos) do
CKAN com :data:`capes_fetcher.catalog.CATALOG`. Os temas do portal são
fatiados em pacotes por era; uma era nova (ex.: ``2025-a-2028``) aparece aqui
como pacote novo, já associada ao tema por prefixo de título quando houver
``package_search``.

O servidor é lento (``package_list`` levou mais de 2 minutos em 2026-11-03,
``package_search`` com 100 pacotes, mais de 4): o ``discover`` não deve rodar em
laço apertado, e uma resposta vazia vira erro em vez de "tudo removido".
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any

from .catalog import CATALOG
from .client import CapesClient

__all__ = ["DiscoverReport", "discover"]


@dataclass
class DiscoverReport:
    """Resultado de :func:`discover`."""

    new_packages: list[dict[str, Any]] = field(default_factory=list)
    removed_packages: list[str] = field(default_factory=list)
    grown_packages: dict[str, dict[str, int]] = field(default_factory=dict)
    known: int = 0

    @property
    def has_changes(self) -> bool:
        """Indica se há algo novo, removido ou crescido em relação ao catálogo."""
        return bool(self.new_packages or self.removed_packages or self.grown_packages)

    def to_dict(self) -> dict[str, Any]:
        """Converte o relatório em dict serializável."""
        data = asdict(self)
        data["has_changes"] = self.has_changes
        return data


def discover(
    packages: Iterable[dict[str, Any] | str] | None = None,
    *,
    client: CapesClient | None = None,
) -> DiscoverReport:
    """Compara o CKAN da CAPES com o catálogo estático.

    Args:
        packages: Pacotes do ``package_search`` (dicts) ou nomes do
            ``package_list`` (str). Se ``None``, consulta ``package_list``.
        client: Cliente da CAPES (usado só quando ``packages`` é ``None``).

    Returns:
        DiscoverReport: Pacotes novos, removidos e (com dicts) crescidos.

    Raises:
        RuntimeError: Se o CKAN não devolver pacotes.
    """
    if packages is None:
        packages = (client or CapesClient()).package_names()
    by_slug: dict[str, dict[str, Any]] = {}
    for item in packages:
        if isinstance(item, str):
            by_slug[item] = {"name": item}
        else:
            by_slug[str(item["name"])] = item
    if not by_slug:
        raise RuntimeError("CKAN da CAPES não devolveu pacotes (portal fora do ar?).")

    report = DiscoverReport()
    for slug, package in sorted(by_slug.items()):
        known = CATALOG.get(slug)
        if known is None:
            report.new_packages.append(
                {
                    "slug": slug,
                    "title": package.get("title", ""),
                    "temas": sorted(
                        g["name"]
                        for g in package.get("groups") or []
                        if g["name"] not in {"educacao", "pesquisa-e-desenvolvimento"}
                    ),
                }
            )
            continue
        report.known += 1
        resources = package.get("resources")
        if resources is not None:
            n_csv = Counter(
                str(r.get("format") or "").strip().upper() for r in resources
            )["CSV"]
            if n_csv > known.n_csv:
                report.grown_packages[slug] = {
                    "n_csv_catalogo": known.n_csv,
                    "n_csv_atual": n_csv,
                }
    report.removed_packages = sorted(set(CATALOG) - set(by_slug))
    return report
