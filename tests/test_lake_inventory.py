"""O inventario do conversor diz a auditoria do lake o que nao vira Parquet."""

from __future__ import annotations

import zipfile
from pathlib import Path

from capes_fetcher.lake import converter

_CURSOS = "AN_BASE;CD_CURSO\n2013;1\n2013;2\n"
_OUTRO = "AN_BASE;CD_CURSO\n2014;1\n2014;3\n"  # mesmo tamanho, outro conteudo


def _plano(raw: Path) -> dict[str, tuple[str | None, str | None]]:
    return {
        p.path.relative_to(raw).as_posix(): (p.dataset, p.skip_reason)
        for p in converter.inventory(raw)
    }


def _csv(raw: Path, nome: str, texto: str) -> None:
    (raw / "cursos").mkdir(parents=True, exist_ok=True)
    (raw / "cursos" / nome).write_text(texto, encoding="utf-8")


def test_inventory_csv_de_conteudo_identico_e_gemeo(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _csv(raw, "cursos_2013@20230126.csv", _CURSOS)
    _csv(raw, "cursos_2016@20230126.csv", _CURSOS)  # identico ao 2013
    _csv(raw, "cursos_2014@20230126.csv", _OUTRO)

    plano = _plano(raw)

    # O primeiro (na ordem do conversor) grava; o identico e gemeo.
    assert plano["cursos/cursos_2013@20230126.csv"] == ("cursos", None)
    assert plano["cursos/cursos_2016@20230126.csv"] == (None, "gemeo")
    # Mesmo tamanho, conteudo diferente: espera Parquet.
    assert plano["cursos/cursos_2014@20230126.csv"] == ("cursos", None)


def test_inventory_gemeo_so_dentro_do_mesmo_dataset(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _csv(raw, "cursos_2013@20230126.csv", _CURSOS)
    (raw / "programas").mkdir()
    (raw / "programas" / "programas_2013@20230126.csv").write_text(_CURSOS)

    plano = _plano(raw)

    assert plano["cursos/cursos_2013@20230126.csv"] == ("cursos", None)
    assert plano["programas/programas_2013@20230126.csv"] == ("programas", None)


def test_inventory_versao_antiga_nao_conta_como_gemeo(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _csv(raw, "cursos_2023@20250324.csv", _CURSOS)  # antiga, de outra versao
    _csv(raw, "cursos_2023@20261105.csv", _OUTRO)
    _csv(raw, "cursos_2022@20250324.csv", _CURSOS)

    plano = _plano(raw)

    assert plano["cursos/cursos_2023@20250324.csv"] == (None, "superado")
    assert plano["cursos/cursos_2023@20261105.csv"] == ("cursos", None)
    # O 2022 seria gemeo do 2023 antigo, mas esse nao e vigente: grava.
    assert plano["cursos/cursos_2022@20250324.csv"] == ("cursos", None)


def test_inventory_zip_identico_e_arquivos_de_apoio(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "teses"
    raw.mkdir(parents=True)
    for nome in ("teses_a@20261101.zip", "teses_b@20261101.zip"):
        with zipfile.ZipFile(raw / nome, "w") as zf:
            zf.writestr("teses_2020.csv", "AN_BASE;X\n2020;1\n")
    (raw / "LEIAME.pdf").write_bytes(b"%PDF")
    (raw / "teses_a@20261101.zip.manifest.json").write_text("{}")

    plano = _plano(raw)

    assert "teses_a@20261101.zip.manifest.json" not in plano
    assert plano["teses_a@20261101.zip"] == (None, None)
    assert plano["teses_b@20261101.zip"] == (None, "gemeo")
    assert plano["LEIAME.pdf"] == (None, "nao_tabular")


def test_inventory_sem_pasta(tmp_path: Path) -> None:
    assert converter.inventory(tmp_path / "nao-existe") == []


def test_inventory_concorda_com_o_conversor(tmp_path: Path) -> None:
    """O gemeo e exatamente o arquivo que o ``convert`` ignora (``skipped``)."""
    raw = tmp_path / "raw"
    _csv(raw, "cursos_2013@20230126.csv", _CURSOS)
    _csv(raw, "cursos_2016@20230126.csv", _CURSOS)
    lake = tmp_path / "lake"
    lake.mkdir()

    res = converter.convert(raw, lake, datasets=["cursos"])

    assert not res.errors
    assert res.converted == 1 and res.skipped == 1
    gemeos = [p for p in converter.inventory(raw) if p.skip_reason == "gemeo"]
    assert [p.path.name for p in gemeos] == ["cursos_2016@20230126.csv"]
    parquets = sorted(p.name for p in (lake / "capes" / "cursos").rglob("*.parquet"))
    assert len(parquets) == 1 and "cursos_2013" in parquets[0]
