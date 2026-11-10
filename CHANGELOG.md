# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.4.0] - 2026-11-09

### Corrigido
- `lake`: em `teses`, `resumo` passa a ser sempre o resumo em português (`DS_RESUMO`) e a nova coluna `abstract` traz o abstract em inglês (`DS_ABSTRACT`). Antes as duas colunas de origem apontavam para `resumo`: nos arquivos de 2013 em diante `resumo` recebia o abstract em inglês e o resumo em português ficava em `ds_resumo`. No layout antigo (1987 a 2012) `resumo` continua vindo de `ResumoTese` e não há `abstract`. **Mudança de contrato:** `abstract` é uma coluna nova, o conteúdo de `resumo` muda de idioma (inglês para português) nos anos de 2013 em diante e `ds_resumo` deixa de existir. **Reconverta `teses`** (veja "Como reconverter" abaixo).
- `lake`: `cursos` e `programas` passam a particionar por `ano` pelo valor da coluna de ano-base (`AN_BASE`), e não pelo ano do nome do arquivo. Antes, `cursos_2013` e `cursos_2015`, que trazem o mesmo conteúdo com `AN_BASE` = 2015, geravam `ano=2013` e `ano=2015` com as mesmas linhas. Quando o nome e a coluna divergem, vale a coluna e a conversão registra um aviso. Quando dois arquivos cobrem exatamente o mesmo conjunto de anos (o arquivo inteiro com o nome errado), o de conteúdo idêntico é ignorado com aviso e o de conteúdo diferente gera erro explícito, sem misturar dados. Anos que apenas se cruzam e a partição de quarentena (ano nulo) não são colisão: cada arquivo grava com a própria chave. **Reconverta `cursos` e `programas`** (veja "Como reconverter" abaixo). Os anos 2013, 2014 e 2016 de `cursos` continuam sem dados: o arquivo publicado com nome 2013 traz o ano-base 2015 e não há arquivos para 2014 e 2016.
- **Como reconverter** (`teses`, `cursos` e `programas`): apague `capes/cursos`, `capes/programas` e `capes/teses` do lake e converta de novo; `--force` não basta. A conversão só remove arquivos antigos da mesma chave, então o parquet anterior ficaria ao lado do novo (por exemplo, `cursos` de 2015 com 12.120 linhas em vez de 6.060, e `ano=2013` ainda com dados de 2015). Atenção: a detecção de colisão entre arquivos vale dentro de uma única execução de `convert()`; uma execução incremental não a detecta contra arquivos já convertidos.

### Adicionado
- Documentação dos dados em `docs/`, conforme a norma de documentação dos dados: página, dicionário de todas as variáveis e esquema de referência para cada um dos três datasets (`teses`, `programas` e `cursos`). Um teste a verifica.

## [0.3.0] - 2026-11-05

### Adicionado
- `check` faz um HEAD curto (2 tentativas, 30 s) por recurso, em vez de 5 tentativas com espera longa; o tempo total cai de ~18 min para menos de 1 min. Se o HEAD falhar, o item usa tamanho e data do CKAN, com caminho estável e ação `download`.
- Downloads com mais tentativas (8) e espera maior entre elas (10 s) diante de 503 do servidor; os padrões continuam sobrescrevíveis por `QUANTILICA_HTTP_ATTEMPTS` e `QUANTILICA_HTTP_RETRY_DELAY`.
- `sync` baixa com 2 downloads paralelos por padrão (antes 4); `--workers` continua valendo.

### Alterado
- A saída do CLI passa a usar o console Rich em vez de `typer.echo`.
- O carimbo do nome do arquivo bruto é a data do `Last-Modified` do arquivo; sem ela, a data do CKAN (`remote_modified`, que viaja no plano); só então a de hoje. Falha no HEAD não produz mais arquivo `@<hoje>`.

### Corrigido
- Recursos multianuais (`programas` e `cursos` de 2013 a 2016) tinham o ano lido da era (2013) e colidiam no mesmo identificador e caminho, com quatro conteúdos diferentes no mesmo arquivo. O ano passa a vir do sufixo `_AAAA` do recurso (`*_2013` a `*_2016`); colisões residuais ganham sufixo estável (pacote e id curto do recurso). Identificadores sem colisão não mudam.

## [0.2.1] - 2026-11-04

### Corrigido
- `lake`: CSV em cp1252 com bytes indefinidos (0x8d, 0x90...) converte em vez de falhar com `'charmap' codec can't decode`; o tratador de erros não reconhecia o encoding que o Python reporta (`charmap`). Os bytes viram o controle C1 de mesmo código, sem perda de linha.

## [0.2.0] - 2026-11-04

### Adicionado
- Catálogo completo por domínio (`catalog_<dominio>.py`, 11 grupos): os 89 pacotes do CKAN (2026-11-03), fatias por era dos 26 temas do portal, com `tier` (`r1` baixa hoje; `listed` = listado, download em release futura). R1 segue com 10 pacotes (teses 4, programas 3, cursos 3); os 79 restantes ficam listados. XLSX (duplicam os CSV), RDF e TTL nunca são baixados.
- `MACRO_ALIASES` (`pos-graduacao`, `bolsas-e-fomento`, `institucional`); `GROUP_ALIASES` agora mapeia para listas.
- `quantilica capes catalogo [grupo] [--tier]` (sem rede) e `quantilica capes discover [--json] [--fail-on-change]` (`capes_fetcher.discover.discover()`): pacotes novos (era nova de um tema) e removidos na fonte; resposta vazia vira erro, nunca "tudo removido".
- `CapesClient.package_names()` (`package_list`).
- O catálogo web de teses (`catalogodeteses.capes.gov.br`, POST, 20 por página) segue fora do fetcher: não serve para coleta em massa.
- Limitação: o servidor é muito lento (`package_list` ~130 s e `package_search` com 100 pacotes ~250 s em 2026-11-03); o `discover` consulta só `package_list`.

### Corrigido
- Política de frescor volta a F2 (`HEAD_FALLBACK_GET`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.
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
- Sem o extra `analysis`, o comando `convert` termina com código 1 e a instrução de instalação (`quantilica install capes --extra analysis`), sem traceback.

## [0.1.0] - 2026-11-01

### Adicionado
- Versão inicial do pacote `capes-fetcher` (`quantilica capes`).
- Suporte a `list`, `check`, `sync` e verificação de frescor via SDK `FetcherApp`.

- Conversor Universal Hive Parquet Lake com `DatasetSpec` em `lake.py`.

