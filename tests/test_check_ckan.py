"""Check sem HEAD (validadores do CKAN), caminho estável e idents únicos."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import pytest
from quantilica.cli.sdk import CheckPlan

from capes_fetcher import catalog, plugin
from capes_fetcher.plugin import fetcher, path_builder

URL = "https://dadosabertos.capes.gov.br/dataset/x/resource/y/download/dados_1990.csv"


def make_entry(**over: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": "teses_1990",
        "base_id": "teses",
        "name": "CAPES-BTD-1990",
        "url": URL,
        "ext": "csv",
        "group": "teses",
        "year": 1990,
        "slug": None,
        "remote_size": 1234,
        "remote_modified": "2021-02-18T18:06:37.847704",
    }
    entry.update(over)
    return entry


@pytest.fixture
def no_network(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    def boom(url: str) -> Any:
        calls.append(url)
        raise OSError("sem rede")

    monkeypatch.setattr(plugin, "_probe_head", boom)
    return calls


def test_check_com_validadores_do_ckan_nao_faz_head(
    tmp_path: Path, no_network: list[str]
) -> None:
    item = fetcher.check_entry(make_entry(), tmp_path)
    assert no_network == []
    assert item.action == "download"
    assert item.reason == "not-present"
    assert item.remote_size == 1234
    assert item.remote_etag is None
    assert item.remote_last_modified == "Thu, 18 Feb 2021 18:06:37 GMT"
    assert item.local_path.endswith("teses/teses_1990@20210218.csv")


def test_check_skip_quando_arquivo_local_existe(
    tmp_path: Path, no_network: list[str]
) -> None:
    entry = make_entry()
    local = path_builder(tmp_path, entry, None)
    local.parent.mkdir(parents=True)
    local.write_bytes(b"x")
    item = fetcher.check_entry(entry, tmp_path)
    assert item.action == "skip-up-to-date"
    assert item.local_exists is True
    assert no_network == []


def test_check_sem_tamanho_head_falho_mantem_caminho_estavel(
    tmp_path: Path, no_network: list[str]
) -> None:
    item = fetcher.check_entry(make_entry(remote_size=None), tmp_path)
    assert no_network == [URL]
    assert item.action == "download"
    assert item.reason.startswith("metadata-unavailable")
    assert item.local_path.endswith("@20210218.csv")
    assert dt.date.today().strftime("%Y%m%d") not in item.local_path


def test_check_sem_tamanho_completa_com_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Head:
        headers = {"ETag": '"abc"', "Content-Length": "999"}

    monkeypatch.setattr(plugin, "_probe_head", lambda url: Head())
    item = fetcher.check_entry(make_entry(remote_size=None), tmp_path)
    assert item.remote_size == 999
    assert item.remote_etag == '"abc"'
    assert item.local_path.endswith("@20210218.csv")


def test_path_builder_prefere_data_do_ckan_ao_head(tmp_path: Path) -> None:
    entry = make_entry()
    a = path_builder(tmp_path, entry, dt.date(2030, 1, 1))
    b = path_builder(tmp_path, entry, None)
    assert a == b
    assert a.name == "teses_1990@20210218.csv"


def test_path_builder_sem_data_do_ckan_usa_head(tmp_path: Path) -> None:
    entry = make_entry(remote_modified=None)
    assert path_builder(tmp_path, entry, dt.date(2022, 5, 6)).name.endswith(
        "@20220506.csv"
    )


def test_entry_serializada_restaura_mesmo_caminho(tmp_path: Path) -> None:
    item = fetcher.check_entry(make_entry(), tmp_path)
    plan = CheckPlan(
        fetcher="capes",
        output_dir=str(tmp_path),
        generated_at="2026-11-05T00:00:00+00:00",
        items=[item],
    )
    restored = CheckPlan.from_json(json.dumps(json.loads(plan.to_json())))
    entry = fetcher.entry_from_plan(dict(restored.items[0].entry))
    # download_entry recalcula com a data do HEAD (diferente): o caminho vale o do check
    assert str(path_builder(tmp_path, entry, dt.date(2030, 1, 1))) == item.local_path


def _fake_package(names: list[str]) -> dict[str, Any]:
    return {
        "resources": [
            {
                "id": f"{i:08x}-aaaa",
                "name": name,
                "format": "CSV",
                "url": f"https://x.invalid/dl/{name.lower()}.csv",
                "size": 10,
                "last_modified": "2020-06-29T20:10:23.570063",
            }
            for i, name in enumerate(names)
        ]
    }


def test_ident_unico_para_recursos_multianuais(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    names = [f"BR-CAPES-CURSO-2013A2016-2020-06-12_{y}" for y in range(2013, 2017)]
    monkeypatch.setattr(
        catalog.CapesClient, "package_show", lambda self, slug: _fake_package(names)
    )
    entries = catalog._entries_for_group("cursos", "cursos", ["pacote-a"])
    assert [e["id"] for e in entries] == [f"cursos_{y}" for y in range(2013, 2017)]
    paths = {path_builder(tmp_path, e, None).name.split("@")[0] for e in entries}
    assert len(paths) == 4


def test_colisao_real_ganha_sufixo_estavel_sem_mudar_os_demais(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    names = ["dados_2020", "dados_2021", "outro_2020", "mais_2020"]
    monkeypatch.setattr(
        catalog.CapesClient, "package_show", lambda self, slug: _fake_package(names)
    )
    entries = catalog._entries_for_group("cursos", "cursos", ["pacote-a"])
    ids = [e["id"] for e in entries]
    assert ids[0] == "cursos_2020"
    assert ids[1] == "cursos_2021"
    assert len(set(ids)) == 4
    assert ids[2] == "cursos_2020_pacote-a"
    assert ids[3].startswith("cursos_2020_pacote-a_")
    assert entries[0]["slug"] is None and entries[1]["slug"] is None
    assert len({path_builder(tmp_path, e, None) for e in entries}) == 4
    # estável entre execuções
    again = catalog._entries_for_group("cursos", "cursos", ["pacote-a"])
    assert [e["id"] for e in again] == ids


def test_ano_do_recurso_teses_inalterado() -> None:
    assert (
        catalog._resource_year("CAPES-BTD-1987-2019-11-01", "u/dados_1987.csv") == 1987
    )
    assert catalog._resource_year("BR-X-2021-2025-03-31", "u/x.csv") == 2021
