"""Tests for capes-fetcher lake converter."""

from __future__ import annotations

import zipfile
from pathlib import Path

import polars as pl
from quantilica.analytics.lake import check_dataset

from capes_fetcher.lake import converter


def test_converter_metadata() -> None:
    """Verify converter source_id and dataset list."""
    assert converter.source_id == "capes"
    datasets = converter.datasets()
    assert "teses" in datasets
    assert "programas" in datasets
    assert "cursos" in datasets


def test_converter_empty_dir(tmp_path: Path) -> None:
    """Test convert with empty input directory."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    res = converter.convert(raw_dir, lake_dir)
    assert res.converted == 0
    assert not res.errors


def test_convert_teses_three_eras(tmp_path: Path) -> None:
    """Test converting teses from all three eras to canonical schema and Hive lake."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    # Era 1 (1987-2012): CamelCase
    csv_era1 = (
        "AnoBase;CodigoPrograma;Autor;TituloTese;Orientador_1;DocumentoDiscente\n"
        "2010;33001P1;JOAO SILVA;ESTUDO DADOS;MARIA OLIVEIRA;12345678900\n"
    )
    (raw_dir / "dados_2010@20261101.csv").write_text(csv_era1, encoding="latin-1")

    # Era 2 (2013-2023): SNAKE_UPPER
    csv_era2 = (
        "AN_BASE;CD_PROGRAMA;NM_AUTOR;NM_PRODUCAO;NM_ORIENTADOR;NR_DOCUMENTO_DISCENTE\n"
        "2018;33001P1;CARLOS PEREIRA;ANALISE SISTEMAS;JOSE SANTOS;98765432100\n"
    )
    file_era2 = raw_dir / "br-capes-btd-2018@20261101.csv"
    file_era2.write_text(csv_era2, encoding="latin-1")

    # Era 3 (2024+): SNAKE_UPPER with CD_ENTIDADE_CAPES
    csv_era3 = (
        "AN_BASE;CD_PROGRAMA;CD_ENTIDADE_CAPES;NM_AUTOR;NM_PRODUCAO;DS_ABSTRACT\n"
        "2024;33001010001P1;10001;ANA SOUZA;INTELIGENCIA ARTIFICIAL;RESUMO EXPANDIDO\n"
    )
    zip_era3 = raw_dir / "br-capes-btd-2024@20261101.zip"
    with zipfile.ZipFile(zip_era3, "w") as zf:
        zf.writestr("br-capes-btd-2024-2025-12-01.csv", csv_era3.encode("latin-1"))

    res = converter.convert(raw_dir.parent, lake_dir)
    assert res.converted == 3
    assert not res.errors

    ds_dir = lake_dir / "capes" / "teses"
    errors = check_dataset(ds_dir)
    assert not errors, f"check_dataset errors: {errors}"

    # Verify partition directories
    p_2010 = ds_dir / "ano=2010"
    p_2018 = ds_dir / "ano=2018"
    p_2024 = ds_dir / "ano=2024"
    assert p_2010.is_dir()
    assert p_2018.is_dir()
    assert p_2024.is_dir()

    # Read each partition and verify canonical schema mapping
    df_2010 = pl.read_parquet(list(p_2010.glob("*.parquet"))[0])
    assert "ano_base" in df_2010.columns
    assert "codigo_programa" in df_2010.columns
    assert "autor" in df_2010.columns
    assert "titulo" in df_2010.columns
    assert "orientador" in df_2010.columns
    assert "documento_discente" in df_2010.columns
    assert df_2010["autor"][0] == "JOAO SILVA"

    df_2018 = pl.read_parquet(list(p_2018.glob("*.parquet"))[0])
    assert "ano_base" in df_2018.columns
    assert "codigo_programa" in df_2018.columns
    assert "autor" in df_2018.columns
    assert "titulo" in df_2018.columns
    assert df_2018["autor"][0] == "CARLOS PEREIRA"

    df_2024 = pl.read_parquet(list(p_2024.glob("*.parquet"))[0])
    assert "ano_base" in df_2024.columns
    assert "codigo_ies" in df_2024.columns
    assert "autor" in df_2024.columns
    assert "titulo" in df_2024.columns
    assert "resumo" in df_2024.columns
    assert df_2024["autor"][0] == "ANA SOUZA"


def test_convert_programas_and_cursos(tmp_path: Path) -> None:
    """Test converting cadastral programas and cursos datasets."""
    raw_dir = tmp_path / "raw" / "pos_graduacao"
    raw_dir.mkdir(parents=True)
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    csv_programas = (
        "AN_BASE;CD_PROGRAMA;NM_PROGRAMA;SG_ENTIDADE_ENSINO\n"
        "2023;33001010001P1;COMPUTACAO;USP\n"
    )
    (raw_dir / "programas_pos_graduacao_2023@20261101.csv").write_text(
        csv_programas, encoding="latin-1"
    )

    csv_cursos = (
        "AN_BASE;CD_CURSO;NM_CURSO;CD_PROGRAMA\n"
        "2023;1001;DOUTORADO EM COMPUTACAO;33001010001P1\n"
    )
    (raw_dir / "cursos_pos_graduacao_2023@20261101.csv").write_text(
        csv_cursos, encoding="latin-1"
    )

    res = converter.convert(raw_dir.parent, lake_dir)
    assert res.converted == 2
    assert not res.errors

    ds_programas = lake_dir / "capes" / "programas"
    assert not check_dataset(ds_programas)
    assert (ds_programas / "ano=2023").is_dir()

    ds_cursos = lake_dir / "capes" / "cursos"
    assert not check_dataset(ds_cursos)
    assert (ds_cursos / "ano=2023").is_dir()


def test_convert_teses_utf8_encoding(tmp_path: Path) -> None:
    """Test that UTF-8 files with non-ASCII characters are parsed without mojibake."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()

    csv_utf8 = (
        "AN_BASE;CD_PROGRAMA;NM_AUTOR;NM_PRODUCAO;NM_ORIENTADOR\n"
        "2024;33001P1;JOSÉ ANTÔNIO DA CONCEIÇÃO;AVALIAÇÃO DE DADOS;MARIA CLÁUDIA\n"
    )
    (raw_dir / "br-capes-btd-2024@20261101.csv").write_text(csv_utf8, encoding="utf-8")

    res = converter.convert(raw_dir.parent, lake_dir)
    assert res.converted == 1
    assert not res.errors

    p = lake_dir / "capes" / "teses" / "ano=2024"
    df = pl.read_parquet(list(p.glob("*.parquet"))[0])
    assert df["autor"][0] == "JOSÉ ANTÔNIO DA CONCEIÇÃO"
    assert df["titulo"][0] == "AVALIAÇÃO DE DADOS"


def _partitions(ds_dir: Path) -> dict[str, int]:
    """Linhas por diretório de partição ``ano=...``."""
    return {
        d.name: sum(pl.read_parquet(f).height for f in d.glob("*.parquet"))
        for d in sorted(ds_dir.glob("ano=*"))
    }


def test_multi_year_csv_is_split_per_row(tmp_path: Path) -> None:
    """Regressão A4: CSV multi-ano era gravado inteiro na partição da 1ª linha."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    csv = (
        "AN_BASE;CD_PROGRAMA;NM_AUTOR;NM_PRODUCAO\n"
        "2019;1;A;T1\n2020;2;B;T2\n2020;3;C;T3\n2021;4;D;T4\n"
    )
    (raw_dir / "br-capes-btd-2019-2021@20261101.csv").write_text(csv, "utf-8")

    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    assert res.converted == 3
    ds = tmp_path / "lake" / "capes" / "teses"
    assert not check_dataset(ds)
    assert _partitions(ds) == {"ano=2019": 1, "ano=2020": 2, "ano=2021": 1}


def test_row_without_valid_year_goes_to_quarantine(tmp_path: Path, caplog) -> None:
    """Linha sem ano válido não ganha ano inventado (antes: fallback 2024)."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    csv = "AN_BASE;CD_PROGRAMA;NM_AUTOR\n2020;1;A\n;2;B\nxx;3;C\n"
    (raw_dir / "br-capes-btd-2020@20261101.csv").write_text(csv, "utf-8")

    with caplog.at_level("WARNING"):
        res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    ds = tmp_path / "lake" / "capes" / "teses"
    parts = _partitions(ds)
    assert parts["ano=2020"] == 1
    assert parts["ano=__HIVE_DEFAULT_PARTITION__"] == 2
    assert "2 linha(s) sem ano valido" in caplog.text


def test_no_year_anywhere_is_an_error_not_2024(tmp_path: Path) -> None:
    """Sem coluna de ano e sem ano no nome: erro contado, nada gravado."""
    raw_dir = tmp_path / "raw" / "pos"
    raw_dir.mkdir(parents=True)
    (raw_dir / "programas_pos_graduacao@20261101.csv").write_text(
        "CD_PROGRAMA;NM_PROGRAMA\n1;X\n", "utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert res.converted == 0
    assert len(res.errors) == 1
    assert not list((tmp_path / "lake").rglob("ano=*"))


def test_year_declared_in_filename_when_no_year_column(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "pos"
    raw_dir.mkdir(parents=True)
    (raw_dir / "programas_pos_graduacao_2022@20261101.csv").write_text(
        "CD_PROGRAMA;NM_PROGRAMA\n1;X\n2;Y\n", "utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    ds = tmp_path / "lake" / "capes" / "programas"
    assert _partitions(ds) == {"ano=2022": 2}


def test_teses_with_both_entity_columns_does_not_collide(tmp_path: Path) -> None:
    """Hipótese do auditor: CD_ENTIDADE_ENSINO e CD_ENTIDADE_CAPES -> codigo_ies."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    csv = (
        "AN_BASE;CD_ENTIDADE_ENSINO;CD_ENTIDADE_CAPES;NM_AUTOR;NM_PRODUCAO\n"
        "2024;ENS1;CAP1;ANA;TITULO\n"
    )
    (raw_dir / "br-capes-btd-2024@20261101.csv").write_text(csv, "utf-8")

    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    p = tmp_path / "lake" / "capes" / "teses" / "ano=2024"
    df = pl.read_parquet(next(p.glob("*.parquet")))
    assert df["codigo_ies"][0] == "ENS1"
    assert df["cd_entidade_capes"][0] == "CAP1"  # nenhuma coluna perdida


def test_zip_with_multiple_members_writes_all(tmp_path: Path) -> None:
    """Cada membro do ZIP é uma origem própria (mesmo sha256 do ZIP)."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    zpath = raw_dir / "br-capes-btd-2018-2019@20261101.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("br-capes-btd-2018.csv", "AN_BASE;NM_AUTOR\n2018;A\n2018;B\n")
        zf.writestr("br-capes-btd-2019.csv", "AN_BASE;NM_AUTOR\n2019;C\n")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    ds = tmp_path / "lake" / "capes" / "teses"
    assert _partitions(ds) == {"ano=2018": 2, "ano=2019": 1}


def test_latin1_csv_decodes_without_replacement_char(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    (raw_dir / "br-capes-btd-2020@20261101.csv").write_bytes(
        "AN_BASE;NM_AUTOR\n2020;JOÃO AÇÃO\n".encode("latin-1")
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors
    p = tmp_path / "lake" / "capes" / "teses" / "ano=2020"
    df = pl.read_parquet(next(p.glob("*.parquet")))
    assert df["autor"][0] == "JOÃO AÇÃO"


def test_reconversion_is_idempotent(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    (raw_dir / "br-capes-btd-2019-2020@20261101.csv").write_text(
        "AN_BASE;NM_AUTOR\n2019;A\n2020;B\n", "utf-8"
    )
    converter.convert(raw_dir.parent, tmp_path / "lake")
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert res.converted == 0
    assert res.skipped == 2
