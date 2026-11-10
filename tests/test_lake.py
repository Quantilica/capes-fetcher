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
    assert "abstract" in df_2024.columns
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


def test_cp1252_com_bytes_indefinidos_nao_quebra(tmp_path: Path) -> None:
    """Bytes 0x8d/0x90 (indefinidos no cp1252, 'charmap codec can't decode') viram
    o controle C1 de mesmo código: sem perda de linha e sem U+FFFD."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    corpo = b"AN_BASE;NM_AUTOR\n1990;JO\xc3O \x8d\n1990;MARIA \x90 A\xc7O\n"
    (raw_dir / "teses_1990@20261101.csv").write_bytes(corpo)
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    ds = tmp_path / "lake" / "capes" / "teses"
    assert _partitions(ds) == {"ano=1990": 2}
    df = pl.read_parquet(next((ds / "ano=1990").glob("*.parquet")))
    assert df["autor"][0].startswith("JOÃO ")
    assert not any("�" in v for v in df["autor"])


def test_teses_sem_coluna_de_ano_usa_ano_do_nome(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    (raw_dir / "teses_1992@20261101.csv").write_bytes(
        b"NM_AUTOR;DS_RESUMO\nJO\xc3O;texto \x8d\n"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "capes" / "teses") == {"ano=1992": 1}


def test_nomes_reais_do_fetcher_programas_e_cursos(tmp_path: Path) -> None:
    """Nomes locais gerados pelo fetcher: ``<base_id>_<ano>@AAAAMMDD.csv``."""
    raw_dir = tmp_path / "raw" / "programas"
    raw_dir.mkdir(parents=True)
    (raw_dir / "programas_2013@20261101.csv").write_bytes(
        b"AN_BASE_PROGRAMA;NM_PROGRAMA\n2013;COMPUTA\xc7\xc3O\n"
    )
    (raw_dir / "cursos_2017@20261101.csv").write_bytes(
        b"NM_CURSO;CD_CURSO\nDOUTORADO;1\n"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "capes" / "programas") == {"ano=2013": 1}
    assert _partitions(tmp_path / "lake" / "capes" / "cursos") == {"ano=2017": 1}


_CURSOS_CSV = "AN_BASE;CD_CURSO;NM_CURSO\n2015;1;MESTRADO A\n2015;2;DOUTORADO B\n"


def test_cursos_particiona_pelo_an_base_da_coluna(tmp_path: Path, caplog) -> None:
    """Dois arquivos com o mesmo conteudo (an_base=2015) e nomes 2013 e 2015:
    a particao vem da coluna, nao do nome, e nao ha duplicacao."""
    raw_dir = tmp_path / "raw" / "cursos"
    raw_dir.mkdir(parents=True)
    for nome in ("cursos_2013@20230126.csv", "cursos_2015@20230126.csv"):
        (raw_dir / nome).write_text(_CURSOS_CSV, encoding="utf-8")
    with caplog.at_level("WARNING"):
        res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "capes" / "cursos") == {"ano=2015": 2}
    assert any("cursos_2013" in r.getMessage() for r in caplog.records)


def test_cursos_nome_diverge_da_coluna_avisa_e_usa_a_coluna(
    tmp_path: Path, caplog
) -> None:
    raw_dir = tmp_path / "raw" / "cursos"
    raw_dir.mkdir(parents=True)
    (raw_dir / "cursos_2013@20230126.csv").write_text(_CURSOS_CSV, encoding="utf-8")
    with caplog.at_level("WARNING"):
        res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "capes" / "cursos") == {"ano=2015": 2}
    assert any("coluna" in r.getMessage() for r in caplog.records)


def test_programas_particiona_pelo_an_base_da_coluna(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "programas"
    raw_dir.mkdir(parents=True)
    (raw_dir / "programas_2014@20230126.csv").write_text(
        "AN_BASE;CD_PROGRAMA_IES\n2016;P1\n", encoding="utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    assert _partitions(tmp_path / "lake" / "capes" / "programas") == {"ano=2016": 1}


def test_mesma_particao_com_conteudo_diferente_e_erro(tmp_path: Path) -> None:
    """Dois arquivos que caem na mesma particao com conteudos diferentes: o
    segundo nao e gravado e o erro e explicito (nada e misturado em silencio)."""
    raw_dir = tmp_path / "raw" / "cursos"
    raw_dir.mkdir(parents=True)
    (raw_dir / "cursos_2013@20230126.csv").write_text(_CURSOS_CSV, encoding="utf-8")
    (raw_dir / "cursos_2015@20230126.csv").write_text(
        "AN_BASE;CD_CURSO;NM_CURSO\n2015;9;OUTRO\n", encoding="utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert len(res.errors) == 1
    assert "ano=2015" in res.errors[0]
    assert _partitions(tmp_path / "lake" / "capes" / "cursos") == {"ano=2015": 2}


def test_teses_separa_resumo_portugues_de_abstract_ingles(tmp_path: Path) -> None:
    """Layout novo (2013+): DS_RESUMO (portugues) -> resumo; DS_ABSTRACT (ingles)
    -> abstract. Nenhuma coluna sobrescreve a outra."""
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    (raw_dir / "teses_2018@20261101.csv").write_text(
        "AN_BASE;NM_PRODUCAO;DS_ABSTRACT;DS_RESUMO\n"
        "2018;TITULO;THIS STUDY APPROACHES;ESTE ESTUDO ABORDA\n",
        encoding="utf-8",
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    df = pl.read_parquet(
        list((tmp_path / "lake" / "capes" / "teses" / "ano=2018").glob("*.parquet"))
    )
    assert df["resumo"][0] == "ESTE ESTUDO ABORDA"
    assert df["abstract"][0] == "THIS STUDY APPROACHES"
    assert "ds_resumo" not in df.columns
    assert "ds_abstract" not in df.columns


def test_teses_layout_antigo_mantem_resumo(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "teses"
    raw_dir.mkdir(parents=True)
    (raw_dir / "teses_2010@20261101.csv").write_text(
        "AnoBase;TituloTese;ResumoTese\n2010;T;RESUMO ANTIGO\n", encoding="utf-8"
    )
    res = converter.convert(raw_dir.parent, tmp_path / "lake")
    assert not res.errors, res.errors
    df = pl.read_parquet(
        list((tmp_path / "lake" / "capes" / "teses" / "ano=2010").glob("*.parquet"))
    )
    assert df["resumo"][0] == "RESUMO ANTIGO"
    assert "abstract" not in df.columns
