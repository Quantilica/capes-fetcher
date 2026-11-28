# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado

- Catálogo: dois pacotes que o CKAN passou a publicar, ambos `listed` (catalogados, sem download): `2021-a-2025-servidores-da-capes` (grupo `gestao`, tema `servidores-da-capes`; CSV de 2021 a 2024 com 355 486 bytes e de 2025-2026 com 85 793) e `2023-a-2025-projetos-de-cooperacao-internacional-pesquisa-scba` (grupo `bolsas`, tema novo `projetos-de-cooperacao-internacional-pesquisa`, da área de bolsas e auxílios; CSV de 2023 com 189 575 bytes, de 2024 com 442 044 e de 2025-2026 com 43 883). Cada pacote traz também o XLSX equivalente e os metadados em PDF e HTML. O catálogo passa de 26 para 27 temas.

### Removido

- Catálogo: três pacotes deixaram de ser públicos no CKAN entre 2026-11-03 (snapshot anterior do catálogo) e 2026-11-28 (o `package_list` não os traz mais e o `package_show` responde 403; confirmado em 2026-11-28; não houve renomeação, fusão em outro pacote nem recurso equivalente em outro pacote da fonte): `2021-a-2025-dotacao-e-execucao-orcamentaria-da-capes` (tema Dotação e Execução Orçamentária; sobra a era `2013-a-2020`), `2023-a-2025-bolsas-dos-mestrados-profissionais-em-rede-nacional-proeb` (sobram as eras até 2022) e `2023-a-2025-bolsistas-da-universidade-aberta-do-brasil-uab` (sobram as eras até 2022). Os três eram `listed`: nunca houve arquivo baixado deles, e o fetcher não apaga nada. Se a fonte os republicar, o `discover` os apontará como pacotes novos.

### Corrigido

- Catálogo: `2023-a-2025-programa-universidade-aberta-do-brasil-uab` ganhou um terceiro CSV (e XLSX) na fonte; a contagem passa de 2 para 3.
- Testes: o `package_list` gravado passa a ser o de 2026-11-28 (88 pacotes) e novos testes provam que um grupo só de pacotes listados nunca consulta a fonte e que um pacote que baixa (teses, programas, cursos) e some do CKAN levanta erro em vez de devolver lista vazia.

## [0.6.0] - 2026-11-28

### Adicionado

- `plugin`: declara `expected_empty_groups` com os 8 grupos que só têm pacotes `listed` (`pessoas`, `producao`, `projetos`, `bolsas`, `formacao-professores`, `fomento`, `periodicos`, `gestao`). Eles são catalogados e nunca baixam; com o `quantilica-cli` 0.30.0, que trata catálogo vazio como erro, sair sem entradas nesses grupos não gera aviso nem erro. Os grupos que baixam (`teses`, `programas`, `cursos`) seguem falhando se esvaziarem. Exige `quantilica-cli>=0.30.0` no host.
- `client`: `pick_package_resources` avisa em WARNING quando dois recursos de formato baixável (CSV ou ZIP) e URLs diferentes dividem o mesmo `name` no CKAN: o core fica com um só por nome e o outro deixava de ser coletado sem aviso. A linha traz o pacote, o nome e as duas URLs. A escolha não mudou. O XLSX que duplica o CSV é a deduplicação esperada e não gera aviso.

### Corrigido

- `client`: `CapesClient.download_resource` chamava `download_with_manifest` com `manifest_path=` e sem `source_id`, `dataset_id` e `producer` (`TypeError` em qualquer chamada real; o teste mockava o método do core). Agora recebe `dataset_id` (obrigatório), `source_id="capes"`, `producer="capes-fetcher"`, `force` e `expected_format` (por padrão, o da extensão do destino, de modo que HTML de bloqueio com HTTP 200 não vira arquivo), e devolve o `Path` baixado, como o core, em vez de um manifesto. Testada com o `download_with_manifest` real sobre transporte simulado. Nada no monorepo a chamava.
- `client`: o cliente da descoberta (`package_list`, `package_show`) deixa de ser um `HttpClient` próprio e passa a ser o cliente padrão do host, que respeita `QUANTILICA_HTTP_*`, `QUANTILICA_SSL_VERIFY` e o bundle de CA. O tempo por requisição fica em no mínimo 300 s (o servidor é lento), salvo `QUANTILICA_HTTP_TIMEOUT`. Sem o host instalado, cai num cliente do core com a verificação TLS lida do ambiente.
- `plugin`: o HEAD de frescor do `check` usa o cliente padrão do host, com o orçamento curto de antes (30 s, 2 tentativas). O orçamento é definido antes de abrir o cliente (`with`): o `__enter__` monta o cliente httpx com o timeout que o objeto tem naquele instante, e mudá-lo depois não o alcançava (a sonda ficava com os 180 s do cliente padrão). O teste confere o timeout efetivo do httpx dentro do `with`.

### Alterado

- Dependência de desenvolvimento: `quantilica-cli>=0.30.0`.

## [0.5.2] - 2026-11-24

### Corrigido

- `lake`: o conversor passa a ter `inventory()`, e a auditoria do lake deixa de acusar `sem_parquet` no CSV que o conversor ignora de propósito por ter conteúdo idêntico ao de outro. O `convert` grava o primeiro arquivo, na ordem dos arquivos vigentes, e conta `skipped` o seguinte, mas a cobertura da auditoria o cobrava. Dentro do mesmo dataset (pelo nome), o arquivo vigente de sha256 igual ao de um que vem antes é declarado `gemeo` (o hash só é calculado entre arquivos do mesmo tamanho). Arquivo que não é ZIP nem CSV é `nao_tabular`; versão antiga de um bruto que tem outra mais nova é `superado` e não entra na comparação; os demais seguem esperando Parquet. O `convert` não muda.
- Correção de uma afirmação da 0.4.0: a CAPES não publica o mesmo arquivo de `cursos` em dois anos. Os quatro recursos do pacote 2013 a 2016 têm cada um o próprio ano-base (2013, 2014, 2015 e 2016). O que se via em `cursos_2013` e `cursos_2015` vinha de coletas anteriores à 0.3.0, que liam o primeiro ano do nome do recurso (2013) e davam o mesmo nome aos quatro arquivos; desde a 0.3.0 cada um tem o seu caminho (`cursos_2013` a `cursos_2016`), agora coberto por teste com os nomes reais dos recursos. Onde a 0.4.0 diz que os anos 2013, 2014 e 2016 de `cursos` "continuam sem dados" por falta de arquivos na fonte, leia: faltavam apenas os arquivos corretos na coleta; a fonte os publica. A documentação de `cursos` foi corrigida no mesmo sentido.

## [0.5.1] - 2026-11-19

### Adicionado

- Testes: identidade do registro conferida.

### Alterado

- CI e infraestrutura alinhados ao template (fetcher-template v0.2.1).

### Corrigido

- `lake`: o build sem mudança não lê mais o bruto. Antes de abrir o ZIP, transcodificar o CSV, varrer as colunas ou calcular o hash do CSV, confere pelos rodapés do lake (`LakeWriter.origin_complete`, que usa o sha256 do sidecar) se o bruto já está em dia e com todas as saídas e, estando, só conta `skipped` pelas saídas declaradas (`origin_outputs`). Cada Parquet declara as saídas do bruto no dataset (a união dos anos de todos os membros): conversão interrompida deixa de virar pulo permanente e lake gravado antes da declaração reconverte uma vez. Membro com erro ou duplicata continua sendo reportado a cada build. O filtro pelo nome vale só para o CSV solto; o ZIP segue roteado pelo rótulo do membro (o nome do ZIP só desempata), e o ZIP que não está completo no dataset tem apenas o diretório central listado, sem extrair nem varrer. A conferência de colisão de partições com outro arquivo segue valendo: o bruto em dia só é aberto se um segundo arquivo cair nas mesmas partições. Mesma contagem de `converted`/`skipped`/`errors`; `force` e bruto novo seguem convertendo. Exige `quantilica-analytics>=0.15.0`.
- `lake`: um bruto em dia cujos anos já foram reivindicados por outro bruto que vem antes na ordem deixa de ser pulado sem conferência; segue o caminho normal e a colisão (erro de conteúdo diferente ou duplicata) é conferida a cada build, como sem o pulo.
- CI: o pyproject declara o PyPI antes do índice Quantilica (`[[tool.uv.index]]`), e o workflow perde `--index` e `--index-strategy`. Com a estratégia padrão `first-index`, o `uv sync` só consulta o índice para o que não está no PyPI (`quantilica-analytics`) e deixa de receber o 503 intermitente que o GitHub Pages devolve a caminhos inexistentes.

## [0.5.0] - 2026-11-10

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, apelidos, órgão, licença, página e cadência) para o registro de fetchers da Quantilica.

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).

### Corrigido
- Os CSVs de teses de 2017 e 2021 (~450 MB cada) falhavam no download com "Operation failed after 8 attempt(s)" (`ReadTimeout` e "peer closed connection"). O servidor da CAPES é lento e instável: às vezes só envia os cabeçalhos depois de minutos (o proxy devolve 504 aos ~300 s, e o timeout de 180 s do cliente estourava antes), entrega esses arquivos a dezenas ou poucas centenas de KB/s e não aceita `Range`, então toda falha recomeça do zero. O timeout de leitura (tempo sem receber bytes) passa de 180 s para 600 s e não há limite total para o download; as tentativas caem de 8 para 6, com espera inicial de 30 s entre elas, para que uma sequência de falhas lentas caiba no prazo da execução agendada. O download também pede o corpo sem compressão (`Accept-Encoding: identity`): com gzip o servidor ora omitia o tamanho do arquivo, o que impedia conferi-lo. Os valores continuam sobrescrevíveis por `QUANTILICA_HTTP_TIMEOUT`, `QUANTILICA_HTTP_ATTEMPTS` e `QUANTILICA_HTTP_RETRY_DELAY`.

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

