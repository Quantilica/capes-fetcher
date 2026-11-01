"""Universal Hive Parquet Lake converter for capes-fetcher."""

from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from collections.abc import Sequence
from pathlib import Path

try:
    import polars as pl
    from quantilica.analytics.lake import ConvertResult, LakeWriter
    from quantilica.core.lake import (
        DatasetDescriptor,
        partition_types_for,
        select_current,
    )
except ImportError as exc:
    raise ImportError(
        "capes_fetcher.lake requer o extra 'analysis': "
        "uv add 'capes-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

SOURCE_ID = "capes"
DATASETS = ["teses", "programas", "cursos"]

TESES_SYNONYMS: dict[str, str] = {
    # Year / base
    "anobase": "ano_base",
    "an_base": "ano_base",
    # Program code / name
    "codigoprograma": "codigo_programa",
    "cd_programa": "codigo_programa",
    "nomeprograma": "nome_programa",
    "nm_programa": "nome_programa",
    # Institution code / name / acronym
    "codigoies": "codigo_ies",
    "cd_entidade_ensino": "codigo_ies",
    "cd_entidade_capes": "codigo_ies",
    "nomeies": "nome_ies",
    "nm_entidade_ensino": "nome_ies",
    "siglaies": "sigla_ies",
    "sg_entidade_ensino": "sigla_ies",
    # Title
    "titulotese": "titulo",
    "titulo_tese": "titulo",
    "nm_producao": "titulo",
    "ds_titulo": "titulo",
    # Author / Student
    "autor": "autor",
    "nm_autor": "autor",
    "nm_discente": "autor",
    "documentodiscente": "documento_discente",
    "nr_documento_discente": "documento_discente",
    # Advisors
    "orientador": "orientador",
    "orientador_1": "orientador",
    "orientador1": "orientador",
    "nm_orientador": "orientador",
    "coorientador": "coorientador",
    "coorientador_1": "coorientador",
    "coorientador1": "coorientador",
    "nm_coorientador": "coorientador",
    # Abstract / Keywords
    "resumotese": "resumo",
    "ds_abstract": "resumo",
    "ds_resumo": "resumo",
    "palavraschave": "palavras_chave",
    "ds_palavra_chave": "palavras_chave",
    # Degree / Level
    "grauacademico": "grau_academico",
    "nm_grau_academico": "grau_academico",
    "nivel": "grau_academico",
    # Areas of knowledge / evaluation
    "grandearea": "grande_area",
    "nm_grande_area_conhecimento": "grande_area",
    "areaconhecimento": "area_conhecimento",
    "nm_area_conhecimento": "area_conhecimento",
    "areaavaliacao": "area_avaliacao",
    "nm_area_avaliacao": "area_avaliacao",
    # Dates and links
    "datadefesa": "data_defesa",
    "dt_titulacao": "data_defesa",
    "dt_defesa": "data_defesa",
    "linktese": "url_texto_completo",
    "ds_url_texto_completo": "url_texto_completo",
}


def _norm_col(col_name: str) -> str:
    s = unicodedata.normalize("NFKD", col_name)
    s = s.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _canonicalize_columns(
    df: pl.DataFrame, mapping: dict[str, str] | None = None
) -> pl.DataFrame:
    """Normalize column names and map known synonyms to canonical schema."""
    renamed = {c: _norm_col(c) for c in df.columns}
    df = df.rename(renamed)
    if mapping:
        canon_map = {c: mapping[c] for c in df.columns if c in mapping}
        if canon_map:
            df = df.rename(canon_map)
    return df


def _read_csv_members(path: Path) -> list[tuple[str, bytes]]:
    """Return list of (member_name, bytes) for CSV in file (or ZIP archive)."""
    try:
        with open(path, "rb") as f:
            header = f.read(4)
        if header.startswith(b"PK"):
            results = []
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    if name.lower().endswith(".csv"):
                        results.append((name, zf.read(name)))
            return results
    except Exception:
        pass

    if path.suffix.lower() == ".csv":
        return [(path.name, path.read_bytes())]
    return []


def _detect_dataset_type(filename: str) -> str | None:
    s = filename.lower()
    if "programa" in s:
        return "programas"
    if "curso" in s:
        return "cursos"
    if "tese" in s or "dissertacao" in s or "btd" in s or "dados_" in s:
        return "teses"
    return None


class CapesLakeConverter:
    """Universal Hive Parquet Lake converter for CAPES datasets."""

    def __init__(self, source_id: str = SOURCE_ID) -> None:
        self.source_id = source_id

    def datasets(self) -> list[str]:
        """Return available dataset identifiers."""
        return list(DATASETS)

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: Sequence[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        res = ConvertResult()
        input_path = Path(input_dir)
        lake_path = Path(lake_dir)

        if not input_path.exists():
            return res

        target_datasets = set(datasets or DATASETS)

        writers: dict[str, LakeWriter] = {}
        for ds in target_datasets:
            if ds not in DATASETS:
                continue
            descriptor = DatasetDescriptor(
                source_id=self.source_id,
                dataset_id=ds,
                alias=ds,
                partition_keys=["ano"],
                partition_types=partition_types_for(["ano"]),
            )
            writers[ds] = LakeWriter(
                lake_path / self.source_id / ds, descriptor, force=force
            )

        all_raw_files = [f for f in input_path.rglob("*") if f.is_file()]
        active_files = select_current(all_raw_files)

        for raw_file in active_files:
            members = _read_csv_members(raw_file)
            if not members:
                continue

            for name, data_bytes in members:
                ds_type = _detect_dataset_type(name) or _detect_dataset_type(
                    raw_file.name
                )
                if not ds_type or ds_type not in writers:
                    continue

                writer = writers[ds_type]
                try:
                    # Decode with latin-1 (standard for CAPES), fallback to utf-8
                    try:
                        text = data_bytes.decode("latin-1")
                    except UnicodeDecodeError:
                        text = data_bytes.decode("utf-8-sig", errors="replace")

                    # Try semicolon separator, fallback to comma
                    sep = ";" if ";" in text[:2000] else ","

                    df = pl.read_csv(
                        io.StringIO(text),
                        separator=sep,
                        infer_schema_length=5000,
                    )
                    if df.height == 0:
                        continue

                    if ds_type == "teses":
                        df = _canonicalize_columns(df, TESES_SYNONYMS)
                    else:
                        df = _canonicalize_columns(df)

                    # Determine year partition
                    if "ano_base" in df.columns:
                        try:
                            ano = int(df["ano_base"].drop_nulls()[0])
                        except Exception:
                            m = re.search(r"(\d{4})", name) or re.search(
                                r"(\d{4})", raw_file.name
                            )
                            ano = int(m.group(1)) if m else 2024
                    else:
                        m = re.search(r"(\d{4})", name) or re.search(
                            r"(\d{4})", raw_file.name
                        )
                        ano = int(m.group(1)) if m else 2024

                    df = df.with_columns(pl.lit(ano).cast(pl.Int32).alias("ano"))

                    writer.write_polars(
                        df,
                        src=raw_file,
                        partitions={"ano": ano},
                    )
                    res.converted += 1
                except Exception as exc:
                    res.errors.append(
                        f"Erro ao converter {name} em {raw_file.name}: {exc}"
                    )

        return res


converter = CapesLakeConverter()
