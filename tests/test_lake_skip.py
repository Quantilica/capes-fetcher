"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import zipfile
from pathlib import Path

import polars as pl
import pytest
import quantilica.core.manifests as manifests_mod
from quantilica.analytics.lake import LakeWriter
from quantilica.core.lake import DatasetDescriptor, partition_types_for

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
        if str(file).startswith(raiz) and not str(file).endswith(".manifest.json"):
            vistas.append(f"open:{file}")
        return original_open(file, *args, **kwargs)

    original_io_open = io.open
    original_path_open = Path.open

    def io_open_espiado(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if str(file).startswith(raiz) and not str(file).endswith(".manifest.json"):
            vistas.append(f"io.open:{file}")
        return original_io_open(file, *args, **kwargs)

    def path_open_espiado(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if str(self).startswith(raiz) and not self.name.endswith(".manifest.json"):
            vistas.append(f"Path.open:{self}")
        return original_path_open(self, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espiado)
    monkeypatch.setattr(io, "open", io_open_espiado)
    monkeypatch.setattr(Path, "open", path_open_espiado)
    monkeypatch.setattr(zipfile, "ZipFile", espia("zipfile", zipfile.ZipFile))
    for nome in ("_member_as_utf8", "_csv_member_names", "_sha256_file"):
        monkeypatch.setattr(lake_mod, nome, espia(nome, getattr(lake_mod, nome)))
    monkeypatch.setattr(pl, "scan_csv", espia("scan_csv", pl.scan_csv))
    monkeypatch.setattr(
        manifests_mod, "sha256_file", espia("hash", manifests_mod.sha256_file)
    )
    return vistas


def _so_lista_zip(leituras: list[str]) -> None:
    """Nada alem de ler o diretorio central do ZIP: sem extrair, transcodificar,
    varrer o CSV nem calcular hash."""
    assert set(leituras) <= {"_csv_member_names", "zipfile"} | {
        v
        for v in leituras
        if v.startswith(("open:", "io.open:")) and v.endswith(".zip")
    }
    for proibido in ("_member_as_utf8", "scan_csv", "_sha256_file", "hash"):
        assert proibido not in leituras


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
    if dataset == "teses":
        assert leituras == []  # o ZIP esta completo no lake: nem e aberto
    else:
        # O ZIP de teses nao tem Parquet neste dataset: so o diretorio dele e
        # listado, para o rotulo do membro valer sobre o nome do ZIP.
        _so_lista_zip(leituras)


def test_um_dataset_nao_toca_o_bruto_de_outro(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    leituras.clear()  # a montagem do bruto de teste le os arquivos
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
    _so_lista_zip(leituras)


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


def _writer(lake: Path, dataset: str) -> LakeWriter:
    return LakeWriter(
        lake / "capes" / dataset,
        DatasetDescriptor(
            source_id="capes",
            dataset_id=dataset,
            alias=dataset,
            partition_keys=["ano"],
            partition_types=partition_types_for(["ano"]),
        ),
    )


def _parquets(lake: Path, dataset: str) -> list[Path]:
    return sorted((lake / "capes" / dataset).rglob("*.parquet"))


def _falha_no_ano_do_zip(monkeypatch: pytest.MonkeyPatch, ano: int) -> None:
    """A escrita do ``ano`` a partir de um ZIP falha, como um disco cheio."""
    original = LakeWriter.write_polars

    def write(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if kwargs["src"].suffix == ".zip" and kwargs["partitions"] == {"ano": ano}:
            raise OSError("disco cheio")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(LakeWriter, "write_polars", write)


def test_conversao_interrompida_no_membro_k_completa_na_rodada_seguinte(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Falha no 2o membro do ZIP (ano 2019): o ZIP nao vira pulo permanente."""
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    with monkeypatch.context() as m:
        _falha_no_ano_do_zip(m, 2019)
        r1 = converter.convert(raw, lake, datasets=["teses"])
    assert len(r1.errors) == 1
    assert "disco cheio" in r1.errors[0]
    assert (r1.converted, r1.skipped) == (3, 0)  # 2018 e os 2 anos do CSV solto

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=["teses"])
    assert r2.errors == []
    assert (r2.converted, r2.skipped) == (1, 3)
    assert "_member_as_utf8" in leituras  # o ZIP foi reaberto
    assert len(_parquets(lake, "teses")) == 4

    leituras.clear()
    r3 = converter.convert(raw, lake, datasets=["teses"])
    assert (r3.converted, r3.skipped, r3.errors) == (0, 4, [])
    assert leituras == []


def test_saidas_declaradas_sao_a_uniao_dos_membros_do_zip(tmp_path: Path) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["teses"])
    zpath = raw / "teses" / "br-capes-btd-2018-2019@20261101.zip"
    writer = _writer(lake, "teses")
    saidas = writer.origin_outputs(zpath)
    assert saidas is not None
    assert sorted(s.split("/")[0] for s in saidas) == ["ano=2018", "ano=2019"]
    assert writer.origin_complete(zpath)


def test_lake_antigo_sem_declaracao_reconverte_uma_vez(
    tmp_path: Path, leituras: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    original = LakeWriter.write_polars

    def sem_declaracao(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        kwargs.pop("origin_outputs", None)
        return original(self, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(LakeWriter, "write_polars", sem_declaracao)
        r0 = converter.convert(raw, lake, datasets=["teses"])
    assert (r0.converted, r0.errors) == (4, [])

    leituras.clear()
    r1 = converter.convert(raw, lake, datasets=["teses"])
    assert (r1.converted, r1.skipped, r1.errors) == (4, 0, [])
    assert "_member_as_utf8" in leituras

    leituras.clear()
    r2 = converter.convert(raw, lake, datasets=["teses"])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 4, [])
    assert leituras == []


def _zip(caminho: Path, **membros: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho, "w") as zf:
        for nome, texto in membros.items():
            zf.writestr(nome, texto)


def test_rotulo_do_membro_vale_sobre_o_nome_do_zip(tmp_path: Path) -> None:
    """ZIP nomeado para cursos com um membro de programas: o dataset do membro
    manda (como no main); o nome do ZIP so desempata membro sem tipo."""
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip(
        raw / "x" / "cursos_pacote@20261101.zip",
        **{
            "programas_2013.csv": "AN_BASE;NM_PROGRAMA\n2013;P\n",
            "dados_2014.csv": "AN_BASE;CD_CURSO\n2014;1\n",
        },
    )
    _sidecars(raw)

    rp = converter.convert(raw, lake, datasets=["programas"])
    assert (rp.converted, rp.skipped, rp.errors) == (1, 0, [])
    rc = converter.convert(raw, lake, datasets=["cursos"])
    # "dados_2014.csv" nao tem tipo proprio de curso: cai em teses pelo "dados_".
    assert (rc.converted, rc.skipped, rc.errors) == (0, 0, [])
    rt = converter.convert(raw, lake, datasets=["teses"])
    assert (rt.converted, rt.skipped, rt.errors) == (1, 0, [])

    rp2 = converter.convert(raw, lake, datasets=["programas"])
    assert (rp2.converted, rp2.skipped, rp2.errors) == (0, 1, [])
    rt2 = converter.convert(raw, lake, datasets=["teses"])
    assert (rt2.converted, rt2.skipped, rt2.errors) == (0, 1, [])


def test_erro_deterministico_de_membro_reaparece_a_cada_build(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip(
        raw / "teses" / "pacote@20261101.zip",
        **{
            "teses_2018.csv": "AN_BASE;NM_AUTOR\n2018;A\n",
            "teses_sem_ano.csv": "NM_AUTOR\nB\n",
        },
    )
    _sidecars(raw)

    r1 = converter.convert(raw, lake, datasets=["teses"])
    assert (r1.converted, len(r1.errors)) == (1, 1)
    r2 = converter.convert(raw, lake, datasets=["teses"])
    assert (r2.converted, r2.skipped, len(r2.errors)) == (0, 1, 1)
    assert "sem coluna de ano-base" in r2.errors[0]


def test_membro_duplicado_no_mesmo_zip_segue_contando_skipped(
    tmp_path: Path,
) -> None:
    """Membro de conteudo igual a outro (mesmos anos): conta skipped a cada build,
    como no main, e o ZIP continua sendo reaberto."""
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    texto = "AN_BASE;NM_AUTOR\n2018;A\n"
    _zip(
        raw / "teses" / "pacote@20261101.zip",
        **{"teses_2018.csv": texto, "teses_2018_copia.csv": texto},
    )
    _sidecars(raw)

    r1 = converter.convert(raw, lake, datasets=["teses"])
    assert (r1.converted, r1.skipped, r1.errors) == (1, 1, [])
    r2 = converter.convert(raw, lake, datasets=["teses"])
    assert (r2.converted, r2.skipped, r2.errors) == (0, 2, [])


def test_bruto_em_dia_que_vem_depois_de_quem_ja_reivindicou_os_anos_da_erro(
    tmp_path: Path,
) -> None:
    """``teses_b_2020`` está no lake; aparece ``teses_a_2020`` (ordenado antes) com
    conteúdo diferente nos mesmos anos. Como no main, o erro de colisão sai em
    todo build e o ``b`` em dia não vira pulo silencioso."""
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    (raw / "teses").mkdir(parents=True)
    (raw / "teses" / "teses_b_2020@20261101.csv").write_text(
        "AN_BASE;NM_AUTOR\n2020;B\n", encoding="utf-8"
    )
    _sidecars(raw)
    r1 = converter.convert(raw, lake, datasets=["teses"])
    assert (r1.converted, r1.skipped, r1.errors) == (1, 0, [])

    (raw / "teses" / "teses_a_2020@20261101.csv").write_text(
        "AN_BASE;NM_AUTOR\n2020;A\n", encoding="utf-8"
    )
    _sidecars(raw)
    r2 = converter.convert(raw, lake, datasets=["teses"])
    assert (r2.converted, r2.skipped, len(r2.errors)) == (1, 0, 1)
    assert "ano=2020" in r2.errors[0] and "teses_a" in r2.errors[0]
    for _ in range(2):
        r = converter.convert(raw, lake, datasets=["teses"])
        assert (r.converted, r.skipped, len(r.errors)) == (0, 1, 1)
        assert "ano=2020" in r.errors[0] and "teses_a" in r.errors[0]
