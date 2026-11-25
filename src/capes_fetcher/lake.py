"""Universal Hive Parquet Lake converter for capes-fetcher."""

from __future__ import annotations

import codecs
import hashlib
import logging
import os
import re
import tempfile
import unicodedata
import zipfile
from collections.abc import Callable, Iterator, Sequence
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import IO

try:
    import polars as pl
    from quantilica.analytics.lake import ConvertResult, LakeWriter, output_id
    from quantilica.core.lake import (
        DatasetDescriptor,
        Planned,
        composite_file_key,
        partition_types_for,
        select_current,
    )
except ImportError as exc:
    raise ImportError(
        "capes_fetcher.lake requer o extra 'analysis': "
        "uv add 'capes-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

logger = logging.getLogger(__name__)

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
    # DS_RESUMO e o resumo em portugues; DS_ABSTRACT, o abstract em ingles.
    "ds_resumo": "resumo",
    "ds_abstract": "abstract",
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


# Colunas de ano-base de qualquer dataset. Em ``teses`` o nome canonico e
# ``ano_base`` (ver ``TESES_SYNONYMS``); em ``programas`` e ``cursos`` o nome
# publicado (``an_base``) e mantido, mas tambem define a particao ``ano``.
_YEAR_COLUMNS = ("ano_base", "an_base")


def _norm_col(col_name: str) -> str:
    s = unicodedata.normalize("NFKD", col_name)
    s = s.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _canonical_rename(
    columns: Sequence[str], mapping: dict[str, str] | None = None
) -> dict[str, str]:
    """Mapa ``coluna original -> nome canonico``, sem colisoes.

    Quando mais de uma coluna do arquivo aponta para o mesmo nome canonico (por
    exemplo ``CD_ENTIDADE_ENSINO`` e ``CD_ENTIDADE_CAPES`` -> ``codigo_ies``), so a
    primeira na ordem do dicionario de sinonimos (deterministica, independe da
    ordem das colunas do arquivo) recebe o nome canonico; as demais mantem o nome
    normalizado, sem perda de dados e sem ``DuplicateError`` do Polars.
    """
    normed = {c: _norm_col(c) for c in columns}
    if not mapping:
        return normed
    order = {syn: i for i, syn in enumerate(mapping)}
    by_canon: dict[str, list[str]] = {}
    for col, norm in normed.items():
        if norm in mapping:
            by_canon.setdefault(mapping[norm], []).append(col)
    result = dict(normed)
    taken = set(normed.values())
    for canon, cols in by_canon.items():
        cols.sort(key=lambda c: order[normed[c]])
        winner, losers = cols[0], cols[1:]
        # O nome canonico ja presente no arquivo (ex.: ``autor``) continua valendo.
        if canon in taken and normed[winner] != canon:
            losers = cols
            winner = None
        if winner is not None:
            result[winner] = canon
        if losers:
            logger.warning(
                "CAPES: colunas %s apontam para o mesmo campo canonico %r; "
                "apenas %s foi renomeada",
                losers + ([winner] if winner else []),
                canon,
                winner or "nenhuma",
            )
    return result


def _canonicalize_columns(
    df: pl.DataFrame, mapping: dict[str, str] | None = None
) -> pl.DataFrame:
    """Normalize column names and map known synonyms to canonical schema."""
    return df.rename(_canonical_rename(df.columns, mapping))


# --- Leitura em streaming ---------------------------------------------------
_CHUNK = 1 << 20
_UTF8 = "utf-8-sig"
_LEGACY = "cp1252"


def _c1_passthrough(exc: UnicodeDecodeError) -> tuple[str, int]:
    """Bytes indefinidos no cp1252 viram o controle C1 de mesmo codigo (sem perda
    e sem U+FFFD). Outros erros continuam erros."""
    # O decodificador cp1252 do Python reporta o erro com encoding "charmap".
    if exc.encoding.lower().replace("-", "").replace("_", "") not in (
        "cp1252",
        "charmap",
    ):
        raise exc
    return "".join(chr(b) for b in exc.object[exc.start : exc.end]), exc.end


codecs.register_error("quantilica_c1", _c1_passthrough)


def _transcode(
    opener: Callable[[], AbstractContextManager[IO[bytes]]], dest: Path, encoding: str
) -> None:
    decoder = codecs.getincrementaldecoder(encoding)(errors="quantilica_c1")
    with opener() as source, open(dest, "w", encoding="utf-8", newline="") as out:
        while chunk := source.read(_CHUNK):
            out.write(decoder.decode(chunk))
        out.write(decoder.decode(b"", final=True))


def _transcode_to_utf8(
    opener: Callable[[], AbstractContextManager[IO[bytes]]], dest: Path
) -> str:
    """Copia o arquivo para ``dest`` em UTF-8, em blocos (memoria constante).

    Encoding explicito: UTF-8 (com ou sem BOM) estrito; se o arquivo nao for UTF-8
    valido, cp1252 (Windows-1252). Nunca ``errors="replace"``. Devolve o encoding
    usado.
    """
    try:
        _transcode(opener, dest, _UTF8)
        return _UTF8
    except UnicodeDecodeError:
        _transcode(opener, dest, _LEGACY)
        return _LEGACY


def _csv_member_names(path: Path) -> list[str] | None:
    """Nomes dos CSVs do ZIP; ``None`` quando ``path`` nao e um ZIP."""
    with open(path, "rb") as f:
        if not f.read(4).startswith(b"PK"):
            return None
    with zipfile.ZipFile(path) as zf:
        return [
            i.filename
            for i in zf.infolist()
            if not i.is_dir() and i.filename.lower().endswith(".csv")
        ]


@contextmanager
def _member_as_utf8(path: Path, name: str | None) -> Iterator[Path]:
    """CSV de um membro (ou do proprio arquivo) em UTF-8 num diretorio temporario.

    ``QUANTILICA_LAKE_SCRATCH`` move o temporario para outro disco.
    """

    @contextmanager
    def opener() -> Iterator[IO[bytes]]:
        if name is None:
            with open(path, "rb") as fh:
                yield fh
        else:
            with zipfile.ZipFile(path) as zf, zf.open(name) as fh:
                yield fh

    with tempfile.TemporaryDirectory(
        dir=os.environ.get("QUANTILICA_LAKE_SCRATCH") or None
    ) as tmp:
        dest = Path(tmp) / "membro.csv"
        _transcode_to_utf8(opener, dest)
        yield dest


def _detect_separator(csv_path: Path) -> str:
    """``;`` se o cabecalho (primeira linha) o contem, senao ``,``."""
    with open(csv_path, encoding="utf-8", newline="") as fh:
        header = fh.readline()
    return ";" if ";" in header else ","


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


_YEAR_TOKEN = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
_ANO_MIN, _ANO_MAX = 1900, 2100


def _declared_year(*names: str) -> int | None:
    """Ano unico declarado no nome do arquivo/membro; ``None`` se nao houver ou se
    houver mais de um (faixa ``2024-2025`` e ambigua e nao vira partição)."""
    for name in names:
        years = {int(y) for y in _YEAR_TOKEN.findall(name.replace("\\", "/"))}
        if len(years) == 1:
            return years.pop()
        if len(years) > 1:
            return None
    return None


def _gemeos(arquivos: Sequence[Path]) -> set[Path]:
    """Arquivos de conteudo identico (sha256) ao de outro que vem antes na ordem.

    So conta dentro do mesmo tipo de dataset (pelo nome): e a regra do conversor,
    que ignora o arquivo cujas particoes e conteudo ja foram gravados por outro
    (``_conferir_colisao``). O primeiro de cada grupo, na ordem dada, e o que
    grava. So se calcula o hash dos que tem o mesmo tamanho.
    """
    por_tamanho: dict[tuple[str | None, int], list[Path]] = {}
    for f in arquivos:
        chave = (_detect_dataset_type(f.name), f.stat().st_size)
        por_tamanho.setdefault(chave, []).append(f)
    gemeos: set[Path] = set()
    for grupo in por_tamanho.values():
        if len(grupo) < 2:
            continue
        vistos: set[str] = set()
        for f in grupo:
            digest = _sha256_file(f)
            if digest in vistos:
                gemeos.add(f)
            vistos.add(digest)
    return gemeos


def _detect_dataset_type(filename: str) -> str | None:
    s = filename.lower()
    if "programa" in s:
        return "programas"
    if "curso" in s:
        return "cursos"
    if "tese" in s or "dissertacao" in s or "btd" in s or "dados_" in s:
        return "teses"
    return None


_HIVE_ANO = "ano="

# Particoes ja gravadas por algum bruto: ``(dataset, anos)`` -> ``(rotulo, sha256
# do CSV)``, ou ``_Adiado`` quando o bruto esta em dia no lake e nao foi aberto.
_Claimed = dict[tuple[str, frozenset[int]], "tuple[str, str | None] | _Adiado"]


@dataclass(frozen=True)
class _Adiado:
    """Particao de um bruto em dia no lake, ainda nao conferida contra outros.

    O build sem mudanca nao le o bruto em dia, mas a conferencia de colisao
    (``claimed``) precisa do sha256 do CSV dele quando um segundo arquivo cai nas
    mesmas particoes. O bruto so e aberto nesse caso (``_resolver_adiado``).
    """

    raw_file: Path
    file_key: str


@dataclass
class _Plano:
    """O que um membro vai gravar: quadro lazy (vale so dentro do ``with`` do CSV
    transcodificado), anos das particoes e rotulo do ano declarado no nome."""

    lf: pl.LazyFrame
    anos: list[int | None]
    valid_years: frozenset[int]
    declared: int | None
    digest: str | None


def _anos_declarados(saidas: Sequence[str]) -> dict[str, set[int]]:
    """``{chave de arquivo: anos}`` das saidas declaradas (``ano=AAAA/<chave>``).

    A quarentena (``ano=__HIVE_DEFAULT_PARTITION__``) nao conta, como ``valid_years``
    na conversao.
    """
    anos: dict[str, set[int]] = {}
    for saida in saidas:
        particao, _, chave = saida.partition("/")
        valor = particao[len(_HIVE_ANO) :] if particao.startswith(_HIVE_ANO) else ""
        if chave and valor.isdigit():
            anos.setdefault(chave, set()).add(int(valor))
    return anos


def _resolver_adiado(adiado: _Adiado) -> tuple[str, str | None]:
    """``(rotulo, sha256 do CSV)`` do membro de um bruto em dia (abre o bruto).

    So e chamado quando outro arquivo cai nas mesmas particoes: o mesmo sha256 que
    a conversao do bruto teria registrado em ``claimed``. ``None`` no digest
    quando o membro nao e encontrado (o chamador trata como conteudo diferente).
    """
    raw_file = adiado.raw_file
    try:
        names = _csv_member_names(raw_file)
        for name in [None] if names is None else names:
            if composite_file_key(raw_file, name).lower() == adiado.file_key:
                with _member_as_utf8(raw_file, name) as csv_path:
                    return name or raw_file.name, _sha256_file(csv_path)
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError):
        pass
    return raw_file.name, None


def _planejar(
    csv_path: Path,
    ds_type: str,
    raw_file: Path,
    label: str,
    *,
    com_digest: bool,
) -> _Plano | None:
    """Quadro com a coluna ``ano`` e os anos que o membro grava; ``None`` se vazio.

    ``com_digest`` calcula o sha256 do CSV (conferencia de colisao), so quando ha
    anos validos.
    """
    # Tudo como texto (convencao do lake): o esquema nao depende de quantas
    # linhas a inferencia viu e codigos nao perdem zeros a esquerda.
    lf = pl.scan_csv(
        csv_path,
        separator=_detect_separator(csv_path),
        infer_schema=False,
        encoding="utf8",
    )
    columns = lf.collect_schema().names()
    rename = _canonical_rename(columns, TESES_SYNONYMS if ds_type == "teses" else None)
    lf = lf.rename(rename)
    if lf.head(1).collect().height == 0:
        return None

    year_col = next(
        (c for c in _YEAR_COLUMNS if c in rename.values()),
        None,
    )
    declared = _declared_year(label, raw_file.name.split("@", 1)[0])
    if year_col is not None:
        # Ano-base por linha: a coluna manda, nao o nome do arquivo. Linha
        # sem ano valido NAO ganha ano inventado: vai para a particao de
        # quarentena (ano nulo).
        ano = (
            pl.col(year_col)
            .str.extract(r"(?:^|\D)(\d{4})(?:\D|$)", 1)
            .cast(pl.Int32, strict=False)
        )
        ano = pl.when(ano.is_between(_ANO_MIN, _ANO_MAX)).then(ano)
    else:
        if declared is None:
            raise ValueError(
                "sem coluna de ano-base e sem ano unico no nome do arquivo: "
                "particao por ano indeterminada"
            )
        ano = pl.lit(declared, dtype=pl.Int32)
    lf = lf.with_columns(ano.cast(pl.Int32).alias("ano"))

    anos = lf.select("ano").unique().collect()["ano"].to_list()
    if year_col is not None and declared is not None and len(anos) == 1:
        if anos[0] is not None and anos[0] != declared:
            logger.warning(
                "CAPES %s: o nome do arquivo diz %d, mas a coluna de "
                "ano-base traz %d; a particao usa o valor da coluna "
                "(ano=%d)",
                label,
                declared,
                anos[0],
                anos[0],
            )
    valid_years = frozenset(y for y in anos if y is not None)
    digest = _sha256_file(csv_path) if com_digest and valid_years else None
    return _Plano(
        lf, sorted(anos, key=lambda y: (y is None, y)), valid_years, declared, digest
    )


class CapesLakeConverter:
    """Universal Hive Parquet Lake converter for CAPES datasets."""

    def __init__(self, source_id: str = SOURCE_ID) -> None:
        self.source_id = source_id

    def datasets(self) -> list[str]:
        """Return available dataset identifiers."""
        return list(DATASETS)

    def inventory(self, input_dir: Path) -> list[Planned]:
        """O que o conversor faz com cada bruto, para a cobertura da auditoria.

        Arquivo que nao seja ZIP ou CSV e ``nao_tabular``; versao antiga de um bruto
        que tem outra mais nova e ``superado``. A CAPES publica, de vez em quando,
        o mesmo CSV em dois anos (``cursos_2016`` identico ao ``cursos_2013``): o
        conversor grava o primeiro e ignora os seguintes, de conteudo identico
        (sha256) no mesmo dataset, e o inventario os declara ``gemeo``, para a
        auditoria nao cobrar Parquet. Os demais devem gerar Parquet.
        """
        input_path = Path(input_dir)
        if not input_path.is_dir():
            return []
        arquivos = [
            f
            for f in sorted(input_path.rglob("*"))
            if f.is_file() and not f.name.endswith((".manifest.json", ".tmp"))
        ]
        dados = [f for f in arquivos if f.suffix.lower() in (".zip", ".csv")]
        vigentes = select_current(dados)
        gemeos = _gemeos(vigentes)
        atuais = set(vigentes)
        tabulares = set(dados)
        planned: list[Planned] = []
        for f in arquivos:
            if f not in tabulares:
                planned.append(Planned(f, skip_reason="nao_tabular"))
            elif f not in atuais:
                planned.append(Planned(f, skip_reason="superado"))
            elif f in gemeos:
                planned.append(Planned(f, skip_reason="gemeo"))
            elif f.suffix.lower() == ".csv":
                planned.append(Planned(f, dataset=_detect_dataset_type(f.name)))
            else:  # ZIP: o dataset sai do nome do membro
                planned.append(Planned(f))
        return planned

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

        # Initialize writers with partition ["ano"]
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

        # (dataset, ano) -> (origem, sha256 do CSV) da primeira origem que gravou
        # a particao; evita duas origens escrevendo o mesmo ano. Um bruto pulado
        # por estar em dia entra como ``_Adiado`` e so e lido se houver colisao.
        claimed: _Claimed = {}

        all_raw_files = [
            f
            for f in input_path.rglob("*")
            if f.is_file() and not f.name.endswith(".manifest.json")
        ]
        active_files = select_current(all_raw_files)

        for raw_file in active_files:
            candidatos = writers
            if raw_file.suffix.lower() == ".csv":
                # CSV solto: o membro e o proprio arquivo, e o dataset sai do nome,
                # sem abrir; sem tipo no nome (ou de outra tarefa) nao e desta
                # tarefa. Em ZIP o nome do MEMBRO manda e o do ZIP so desempata, e
                # so se sabe listando o diretorio do ZIP: nao se filtra pelo nome.
                alvo = _detect_dataset_type(raw_file.name)
                if not alvo or alvo not in writers:
                    continue
                candidatos = {alvo: writers[alvo]}
            # Completo no lake: o bruto igual ao registrado nos rodapes, com TODAS
            # as saidas que declarou (um Parquet por membro e ano), e pulado antes
            # de abrir o ZIP, transcodificar ou calcular hash do CSV (o bruto pode
            # estar numa montagem lenta). ``skipped`` e o numero de saidas
            # declaradas, o mesmo que o laco abaixo contaria. Um build
            # interrompido deixa saidas faltando e o bruto e reaberto.
            pendentes: dict[str, LakeWriter] = {}
            for ds, w in candidatos.items():
                if not force and w.origin_complete(raw_file):
                    saidas = w.origin_outputs(raw_file) or []
                    # Anos ja reivindicados por outro bruto que veio antes na
                    # ordem: a colisao tem de ser conferida (erro ou duplicata),
                    # entao o bruto segue o caminho normal, como sem o pulo.
                    if not self._colide_com_reivindicado(claimed, ds, saidas):
                        res.skipped += len(saidas)
                        self._adiar_particoes(claimed, ds, raw_file, saidas)
                        continue
                pendentes[ds] = w
            if not pendentes:
                continue

            try:
                names = _csv_member_names(raw_file)
            except (OSError, zipfile.BadZipFile) as exc:
                res.errors.append(f"CAPES {raw_file.name}: ZIP ilegivel: {exc}")
                continue
            if names is None:  # CSV solto, sem ZIP
                if raw_file.suffix.lower() != ".csv":
                    continue
                members: list[str | None] = [None]
            else:
                members = list(names)

            # Membros por dataset, na ordem do ZIP.
            por_dataset: dict[str, list[str | None]] = {}
            for name in members:
                label = name or raw_file.name
                ds_type = _detect_dataset_type(label) or _detect_dataset_type(
                    raw_file.name
                )
                if ds_type and ds_type in pendentes:
                    por_dataset.setdefault(ds_type, []).append(name)

            for ds_type, membros in por_dataset.items():
                self._convert_dataset(
                    pendentes[ds_type], ds_type, raw_file, membros, claimed, res
                )

        return res

    @staticmethod
    def _colide_com_reivindicado(
        claimed: _Claimed, ds_type: str, saidas: Sequence[str]
    ) -> bool:
        """Algum membro do bruto em dia cobre os mesmos anos de um já reivindicado."""
        return any(
            (ds_type, frozenset(valores)) in claimed
            for valores in _anos_declarados(saidas).values()
        )

    @staticmethod
    def _adiar_particoes(
        claimed: _Claimed, ds_type: str, raw_file: Path, saidas: Sequence[str]
    ) -> None:
        """Registra em ``claimed`` os anos de cada membro de um bruto em dia.

        Os anos vem das saidas declaradas (``ano=AAAA/<chave>``), sem ler o lake;
        o sha256 do CSV so e calculado se houver colisao (``_resolver_adiado``).
        """
        for chave, valores in _anos_declarados(saidas).items():
            claimed.setdefault((ds_type, frozenset(valores)), _Adiado(raw_file, chave))

    def _convert_dataset(
        self,
        writer: LakeWriter,
        ds_type: str,
        raw_file: Path,
        membros: list[str | None],
        claimed: _Claimed,
        res: ConvertResult,
    ) -> None:
        """Converte os membros de um bruto que caem num dataset.

        Cada Parquet declara TODAS as saidas do bruto no dataset (a uniao dos anos
        de todos os membros gravados), para o proximo build so pular o bruto
        quando nenhuma faltar. Com mais de um membro as saidas so se conhecem
        planejando todos antes da primeira escrita (uma passada a mais); com um so,
        a mesma passada planeja e grava. Membro que da erro, ou que e duplicata de
        outro (``skipped``), deixa o bruto sem declaracao: segue sendo reaberto e
        o erro/contagem se repete a cada build, como sempre.
        """
        saidas: list[str] | None = None
        escrever = membros
        if len(membros) > 1:
            uniao: set[str] = set()
            escrever = []
            limpo = True
            for name in membros:
                label = name or raw_file.name
                key = composite_file_key(raw_file, name).lower()
                try:
                    with _member_as_utf8(raw_file, name) as csv_path:
                        plano = _planejar(
                            csv_path, ds_type, raw_file, label, com_digest=True
                        )
                        decisao = self._conferir_colisao(
                            plano, ds_type, label, claimed, res
                        )
                except Exception as exc:
                    limpo = False
                    res.errors.append(
                        f"Erro ao converter {label} em {raw_file.name}: {exc}"
                    )
                    continue
                if decisao == "duplicado":
                    limpo = False
                elif plano is not None:
                    escrever.append(name)
                    uniao.update(output_id({"ano": y}, key) for y in plano.anos)
            saidas = sorted(uniao) if limpo and uniao else None

        for name in escrever:
            label = name or raw_file.name
            # Cada membro e uma origem propria no lake (chave composta
            # zip+membro): o sha256 do ZIP e o mesmo para todos os membros.
            key = composite_file_key(raw_file, name).lower()
            try:
                with _member_as_utf8(raw_file, name) as csv_path:
                    plano = _planejar(
                        csv_path,
                        ds_type,
                        raw_file,
                        label,
                        com_digest=len(membros) == 1,
                    )
                    if plano is None:
                        continue
                    declaradas = saidas
                    if len(membros) == 1:
                        if (
                            self._conferir_colisao(plano, ds_type, label, claimed, res)
                            == "duplicado"
                        ):
                            continue
                        declaradas = [output_id({"ano": y}, key) for y in plano.anos]
                    self._escrever_anos(
                        writer, raw_file, key, plano, label, declaradas, res
                    )
            except Exception as exc:
                res.errors.append(
                    f"Erro ao converter {label} em {raw_file.name}: {exc}"
                )

    @staticmethod
    def _conferir_colisao(
        plano: _Plano | None,
        ds_type: str,
        label: str,
        claimed: _Claimed,
        res: ConvertResult,
    ) -> str:
        """``"gravar"``, ``"duplicado"`` (conteudo igual ao de outro; conta
        ``skipped``) ou levanta ``ValueError`` (mesmas particoes, conteudo diferente).

        Colisao so quando dois arquivos cobrem exatamente os mesmos anos (arquivo
        inteiro com o nome errado). Anos que apenas se cruzam e a particao de
        quarentena (ano nulo) nao contam: cada arquivo grava com a propria chave e
        nao sobrescreve o outro.
        """
        if plano is None or not plano.valid_years:
            return "gravar"
        other = claimed.get((ds_type, plano.valid_years))
        if isinstance(other, _Adiado):
            other = _resolver_adiado(other)
        anos_txt = ", ".join(str(y) for y in sorted(plano.valid_years))
        if other is not None:
            if other[1] == plano.digest:
                logger.warning(
                    "CAPES %s: conteudo identico a %s, que ja gravou ano=%s; "
                    "arquivo ignorado",
                    label,
                    other[0],
                    anos_txt,
                )
                res.skipped += 1
                return "duplicado"
            raise ValueError(
                f"as particoes ano={anos_txt} de {ds_type} ja foram "
                f"gravadas por {other[0]} com conteudo diferente; confira "
                "o ano-base dos dois arquivos"
            )
        claimed[(ds_type, plano.valid_years)] = (label, plano.digest or "")
        return "gravar"

    @staticmethod
    def _escrever_anos(
        writer: LakeWriter,
        raw_file: Path,
        key: str,
        plano: _Plano,
        label: str,
        declaradas: list[str] | None,
        res: ConvertResult,
    ) -> None:
        """Escreve um membro, uma particao ``ano`` por vez (lazy, streaming)."""
        for year in plano.anos:
            part = plano.lf.filter(
                pl.col("ano").is_null() if year is None else pl.col("ano") == year
            )
            if year is None:
                n = part.select(pl.len()).collect().item()
                logger.warning(
                    "CAPES %s: %d linha(s) sem ano valido na particao de "
                    "quarentena ano=__HIVE_DEFAULT_PARTITION__",
                    label,
                    n,
                )
            written = writer.write_polars(
                part,
                src=raw_file,
                partitions={"ano": year},
                file_key_name=key,
                origin_outputs=declaradas,
            )
            if written.status == "skipped":
                res.skipped += 1
            else:
                res.converted += 1


converter = CapesLakeConverter()
