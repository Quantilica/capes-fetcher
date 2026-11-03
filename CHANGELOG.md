# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido
- Aliases de grupo (`sync padrao` etc.): o `FetcherApp` recebia `alias -> str` e o
  SDK fazia `list("teses")`, resolvendo para `['t', 'e', 's', ...]` ("Grupo
  desconhecido: 't'"). O plugin agora passa `alias -> [grupo]`.
- `lake`: a partição `ano` agora é por linha (`ano_base`), não mais o ano da
  primeira linha do arquivo; CSV multi-ano gera uma partição por ano. Linha sem
  ano válido vai para `ano=__HIVE_DEFAULT_PARTITION__` com aviso de contagem
  (antes recebia 2024 em silêncio); sem `ano_base`, só um ano único declarado no
  nome do arquivo é aceito, senão o arquivo vira erro.
- `lake`: cada membro de ZIP é uma origem própria (`composite_file_key`);
  leitura em streaming (transcodificação em blocos para UTF-8/cp1252 explícito +
  `scan_csv` lazy), sem `read_bytes`/`StringIO`; colunas lidas como texto.
- `lake`: cabeçalhos com `CD_ENTIDADE_ENSINO` e `CD_ENTIDADE_CAPES` juntos
  quebravam (`codigo_ies` duplicada); só uma recebe o nome canônico e a outra
  mantém o nome normalizado.
- `tests/test_plugin.py::test_cli_list` não acessa mais a rede (catálogo
  mockado); testes de rede usam `@pytest.mark.network` e ficam fora do
  `pytest -q` padrão.
- `sync` passa a baixar os CSVs reais: o catálogo gerava ids inexistentes
  (`teses_2021`) e baixaria o JSON do pacote. Agora descobre os pacotes no CKAN
  e expande um recurso por ano.
- `CAPES_CKAN_URL` aponta para a raiz do portal (o `CkanClient` já acrescenta
  `/api/3`).

## [0.1.0] - 2026-11-01

### Adicionado
- Versão inicial do pacote `capes-fetcher` (`quantilica capes`).
- Suporte a `list`, `check`, `sync` e verificação de frescor via SDK `FetcherApp`.

- Conversor Universal Hive Parquet Lake com `DatasetSpec` em `lake.py`.

