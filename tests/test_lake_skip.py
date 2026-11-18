"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import builtins
import hashlib
import json
import zipfile
from pathlib import Path

import polars as pl
import pytest
import quantilica.core.manifests as manifests_mod

import capes_fetcher.lake as lake_mod
from capes_fetcher.lake import converter

_TESES = "AN_BASE;NM_AUTOR\n{a};A\n{b};B\n"
_CURSOS = "AN_BASE;CD_CURSO;NM_CURSO\n2015;1;MESTRADO A\n2015;2;DOUTORADO B\n"


def _sidecars(raiz: Path) -> None:
    """Sidecar ``.manifest.json`` com o sha256 de cada bruto, como o fetcher grava:
    o hash do bruto sai dele, sem ler o arquivo."""
    for f in sorted(raiz.rglob("*")):
        if f.is_file() and not f.name.endswith(".manifest.json"):
            Path(f"{f}.manifest.json").write_text(
                json.dumps(
                    {
                        "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                        "size_bytes": f.stat().st_size,
                    }
                ),
                encoding="utf-8",
            )


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    (raw / "teses").mkdir(parents=True)
    (raw / "programas").mkdir()
    (raw / "cursos").mkdir()
    with zipfile.ZipFile(
        raw / "teses" / "br-capes-btd-2018-2019@20261101.zip", "w"
    ) as zf:
        zf.writestr("br-capes-btd-2018.csv", "AN_BASE;NM_AUTOR\n2018;A\n2018;B\n")
        zf.writestr("br-capes-btd-2019.csv", "AN_BASE;NM_AUTOR\n2019;C\n")
    (raw / "teses" / "teses_2020@20261101.csv").write_text(
        _TESES.format(a=2020, b=2021), encoding="utf-8"
    )
    (raw / "programas" / "programas_2013@20261101.csv").write_bytes(
        b"AN_BASE_PROGRAMA;NM_PROGRAMA\n2013;COMPUTA\xc7\xc3O\n"
    )
    (raw / "cursos" / "cursos_2017@20261101.csv").write_text(
        "AN_BASE;CD_CURSO\n2017;1\n", encoding="utf-8"
    )
    _sidecars(raw)
    return raw


@pytest.fixture
def leituras(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[str]:
    """Registra toda abertura/leitura do bruto: ZIP, open, transcodificação, scan."""
    vistas: list[str] = []
    raiz = str(tmp_path / "raw")

    def espia(nome: str, original):  # noqa: ANN001, ANN202
        def _f(*args, **kwargs):  # noqa: ANN002, ANN003
            vistas.append(nome)
            return original(*args, **kwargs)

        return _f

    original_open = builtins.open

    def open_espiado(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if str(file).startswith(raiz):
            vistas.append(f"open:{file}")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espiado)
    monkeypatch.setattr(zipfile, "ZipFile", espia("zipfile", zipfile.ZipFile))
    for nome in ("_member_as_utf8", "_csv_member_names", "_sha256_file"):
        monkeypatch.setattr(lake_mod, nome, espia(nome, getattr(lake_mod, nome)))
    monkeypatch.setattr(pl, "scan_csv", espia("scan_csv", pl.scan_csv))
    monkeypatch.setattr(
        manifests_mod, "sha256_file", espia("hash", manifests_mod.sha256_file)
    )
    return vistas


@pytest.mark.parametrize(
    ("dataset", "convertidos"),
    [("teses", 4), ("programas", 1), ("cursos", 1)],
)
def test_segunda_rodada_nao_le_o_bruto(
    tmp_path: Path, leituras: list[str], dataset: str, convertidos: int
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"

    r1 = converter.convert(raw, lake, datasets=[dataset])
    assert not r1.errors
    assert (r1.converted, r1.skipped) == (convertidos, 0)
    assert leituras  # a primeira rodada le o bruto

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=[dataset])
    assert (r2.converted, r2.skipped, r2.errors) == (0, convertidos, [])
    assert leituras == []


def test_um_dataset_nao_toca_o_bruto_de_outro(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["cursos"])
    assert not any(n in v for v in leituras for n in ("teses_2020", "programas_2013"))


def test_todos_os_datasets_em_dia_nao_extrai_nem_le_o_csv(
    tmp_path: Path, leituras: list[str]
) -> None:
    """Sem ``datasets``, o ZIP nomeado para teses so tem o diretorio listado (nao
    se sabe, sem abri-lo, que nao tem membros de programas/cursos); nenhum
    membro e extraido, transcodificado, varrido ou tem o hash calculado."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    r1 = converter.convert(raw, lake)
    assert not r1.errors
    leituras.clear()

    r2 = converter.convert(raw, lake)
    assert (r2.converted, r2.skipped, r2.errors) == (0, r1.converted, [])
    assert set(leituras) <= {"_csv_member_names", "zipfile"} | {
        v for v in leituras if v.startswith("open:") and v.endswith(".zip")
    }
    assert "_member_as_utf8" not in leituras
    assert "scan_csv" not in leituras
    assert "_sha256_file" not in leituras


def test_force_reconverte(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["teses"])
    leituras.clear()

    r = converter.convert(raw, lake, datasets=["teses"], force=True)
    assert (r.converted, r.skipped, r.errors) == (4, 0, [])
    assert "_member_as_utf8" in leituras


def test_bruto_novo_converte_e_o_antigo_segue_em_dia(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["teses"])

    (raw / "teses" / "teses_2022@20261201.csv").write_text(
        _TESES.format(a=2022, b=2022), encoding="utf-8"
    )
    _sidecars(raw)
    leituras.clear()

    r = converter.convert(raw, lake, datasets=["teses"])
    assert (r.converted, r.skipped, r.errors) == (1, 4, [])
    # Do bruto, so o arquivo novo foi aberto.
    abertos = [v for v in leituras if v.startswith("open:")]
    assert abertos
    assert all("teses_2022" in v for v in abertos)
    assert "_csv_member_names" in leituras

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=["teses"])
    assert (r3.converted, r3.skipped, r3.errors) == (0, 5, [])
    assert leituras == []


def test_bruto_alterado_no_lugar_reconverte(tmp_path: Path) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["teses"])

    (raw / "teses" / "teses_2020@20261101.csv").write_text(
        _TESES.format(a=2020, b=2020) + "2020;C\n", encoding="utf-8"
    )
    r = converter.convert(raw, lake, datasets=["teses"])
    assert not r.errors
    assert r.converted == 1  # so o ano 2020
    assert r.skipped == 2


def test_colisao_com_bruto_em_dia_segue_sendo_erro(tmp_path: Path) -> None:
    """Dois CSVs nos mesmos anos, conteudos diferentes: o segundo e erro, e o
    bruto em dia (pulado pelos rodapes) ainda vale como o primeiro a gravar."""
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    (raw / "cursos").mkdir(parents=True)
    (raw / "cursos" / "cursos_2013@20230126.csv").write_text(_CURSOS, "utf-8")
    (raw / "cursos" / "cursos_2015@20230126.csv").write_text(
        "AN_BASE;CD_CURSO;NM_CURSO\n2015;9;OUTRO\n", "utf-8"
    )
    r1 = converter.convert(raw, lake)
    r2 = converter.convert(raw, lake)
    assert (r1.converted, r1.skipped, len(r1.errors)) == (1, 0, 1)
    assert (r2.converted, r2.skipped, len(r2.errors)) == (0, 1, 1)
    assert "ano=2015" in r2.errors[0]
    parquets = sorted((lake / "capes" / "cursos").rglob("*.parquet"))
    assert [p.parent.name for p in parquets] == ["ano=2015"]


def test_colisao_identica_com_bruto_em_dia_segue_sendo_skipped(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    (raw / "cursos").mkdir(parents=True)
    (raw / "cursos" / "cursos_2013@20230126.csv").write_text(_CURSOS, "utf-8")
    (raw / "cursos" / "cursos_2015@20230126.csv").write_text(_CURSOS, "utf-8")
    r1 = converter.convert(raw, lake)
    r2 = converter.convert(raw, lake)
    assert (r1.converted, r1.skipped, r1.errors) == (1, 1, [])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])
    assert len(list((lake / "capes" / "cursos").rglob("*.parquet"))) == 1
