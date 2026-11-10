---
dataset:
  id: programas
  fonte: capes
  titulo: Programas de pós-graduação stricto sensu
  resumo: Programas de pós-graduação stricto sensu do Brasil por ano-base, com instituição, localização, área de conhecimento e de avaliação, conceito e situação.
  orgao: Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES)
  pagina_oficial: https://dadosabertos.capes.gov.br/dataset/2021-a-2024-programas-da-pos-graduacao-stricto-sensu-no-brasil
  licenca: "Creative Commons Attribution (CC BY), conforme os pacotes de programas no portal de dados abertos da CAPES: http://www.opendefinition.org/licenses/cc-by"
  periodicidade: anual, com atualização em geral no primeiro semestre de cada ano, segundo o metadado oficial
  cobertura: {inicio: "2013", fim: em-curso}
  unidade: um programa de pós-graduação stricto sensu em um ano-base
  granularidade: {espacial: município sede do programa (com UF e região), temporal: ano-base}
  formato_bruto: "CSV por ano-base, separador ponto e vírgula, texto em Windows-1252 (nenhum arquivo conferido é UTF-8), uma linha de cabeçalho"
  lake: {estado: convertido, particoes: [ano], chave: [ano, cd_programa_ies], colunas: 34}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras:
    - {desde: "2013-01", mudanca: "Primeiro layout (32 colunas): ano de início do programa em ANO_INICIO_PROGRAMA e coluna DS_CLIENTELA_QUADRIENAL_2017 (participação na Avaliação Quadrienal 2017)"}
    - {desde: "2017-01", mudanca: "Segundo layout (32 colunas): ANO_INICIO_PROGRAMA passa a AN_INICIO_PROGRAMA, entra NM_AREA_BASICA e sai DS_CLIENTELA_QUADRIENAL_2017"}
  revisado_em: 2026-11-09
  versao_fetcher: 0.3.0
---

# Programas de pós-graduação stricto sensu

## Resumo

Cadastro anual dos programas de pós-graduação stricto sensu reconhecidos no país: instituição de ensino, município e UF sede, modalidade (acadêmico ou profissional), grau, áreas de conhecimento e de avaliação, conceito (nota), situação e se o programa é em rede. A CAPES o produz a partir da coleta na Plataforma Sucupira. Serve para contar programas por região, área, natureza da instituição e conceito, e para ligar teses e cursos aos programas.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `capes/programas` |
| Órgão | Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) |
| Página oficial | https://dadosabertos.capes.gov.br/dataset/2021-a-2024-programas-da-pos-graduacao-stricto-sensu-no-brasil |
| Licença | Creative Commons Attribution (CC BY), conforme os pacotes de programas no portal de dados abertos da CAPES: http://www.opendefinition.org/licenses/cc-by |
| Periodicidade | anual, com atualização em geral no primeiro semestre de cada ano, segundo o metadado oficial |
| Cobertura | 2013 a em-curso |
| Unidade (uma linha) | um programa de pós-graduação stricto sensu em um ano-base |
| Granularidade | espacial: município sede do programa (com UF e região); temporal: ano-base |
| Formato bruto | CSV por ano-base, separador ponto e vírgula, texto em Windows-1252 (nenhum arquivo conferido é UTF-8), uma linha de cabeçalho |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `ano`, `cd_programa_ies` |
| Colunas | 34 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | 2013-01: Primeiro layout (32 colunas): ano de início do programa em ANO_INICIO_PROGRAMA e coluna DS_CLIENTELA_QUADRIENAL_2017 (participação na Avaliação Quadrienal 2017); 2017-01: Segundo layout (32 colunas): ANO_INICIO_PROGRAMA passa a AN_INICIO_PROGRAMA, entra NM_AREA_BASICA e sai DS_CLIENTELA_QUADRIENAL_2017 |
| Revisado em | 2026-11-09 |
| Versão do fetcher | 0.3.0 |

## Origem e coleta

- O fetcher baixa os CSVs dos pacotes "Programas da Pós-Graduação Stricto Sensu do Brasil" do portal de dados abertos da CAPES: 2013 a 2016, 2017 a 2020 e 2021 a 2024. Cada pacote traz um CSV e um XLSX por ano-base e arquivos RDF/TTL de apoio; o fetcher usa só o CSV.
- No bruto, cada ano é `programas_<AAAA>@<AAAAMMDD>.csv`, em que o sufixo é a data da última modificação do arquivo na fonte (`Last-Modified`), ou, sem ela, a data do CKAN.
- Conferido em 2026-11-09 pela listagem do bruto: 12 arquivos, de 2013 a 2024, um por ano, sem lacunas.

## Conteúdo

- Unidade de análise: um programa em um ano-base. Programas em rede aparecem uma vez, sob a instituição principal; as demais ficam em `sg_entidade_ensino_rede`.
- Cobertura anunciada pela fonte: 2013 a 2024, em três pacotes. Número de programas, pelo metadado oficial: 3.568 em 2013, 3.765 em 2014, 3.946 em 2015, 4.186 em 2016, 4.709 em 2021, 4.594 em 2022, 4.659 em 2023 e 4.635 em 2024. Nos arquivos de 2013, 2021 e 2024 as linhas conferem com esses números (3.568, 4.709 e 4.635).
- Cada linha é uma "foto" do programa: a fonte explica que só a última imagem homologada de cada programa vale para a avaliação e que programas podem retificar dados depois.
- Eras: veja o cabeçalho. O arquivo de 2013 tem `ano_inicio_programa` e `ds_clientela_quadrienal_2017`; os de 2021 e 2024 têm `an_inicio_programa` e `nm_area_basica`. Os arquivos de 2014 a 2016 têm o mesmo cabeçalho que o de 2013, e os de 2017 a 2024 o mesmo que o de 2021 (cabeçalhos conferidos na listagem do bruto).

## Variáveis

Descrições dos metadados oficiais da CAPES (versões 2013 a 2016 e 2021 a 2024); onde a fonte não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto. Período: P1 é 2013 a 2016 e P2 é 2017 em diante.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ano` | `AN_BASE` (valor da coluna) | inteiro (partição) | Ano da partição, tirado do ano-base de cada linha (`an_base`); o ano do nome do arquivo só vale se o arquivo não tiver essa coluna. Coincide com o ano do nome nos arquivos conferidos | ano de 4 dígitos | todos |
| `an_base` | `AN_BASE` | texto | Ano de referência das atividades declaradas pelo programa | ano de 4 dígitos | todos |
| `nm_grande_area_conhecimento` | `NM_GRANDE_AREA_CONHECIMENTO` | texto | Nome da grande área de conhecimento do programa | 9 valores na amostra de 2024 | todos |
| `nm_area_conhecimento` | `NM_AREA_CONHECIMENTO` | texto | Nome da área de conhecimento do programa | — | todos |
| `nm_area_basica` | `NM_AREA_BASICA` | texto | Menor nível de área do conhecimento especificado pelo programa no ato da proposta | — | P2 |
| `nm_subarea_conhecimento` | `NM_SUBAREA_CONHECIMENTO` | texto | Nome da subárea de conhecimento do programa | `NÃO SE APLICA` quando não se aplica | todos |
| `nm_especialidade` | `NM_ESPECIALIDADE` | texto | Nome da especialidade do conhecimento do programa | `NÃO SE APLICA` quando não se aplica | todos |
| `cd_area_avaliacao` | `CD_AREA_AVALIACAO` | texto | Código identificador da área de avaliação do programa | número, como texto | todos |
| `nm_area_avaliacao` | `NM_AREA_AVALIACAO` | texto | Nome da área de avaliação do programa | — | todos |
| `cd_entidade_capes` | `CD_ENTIDADE_CAPES` | texto | Código da instituição de ensino superior na CAPES | 8 dígitos | todos |
| `cd_entidade_emec` | `CD_ENTIDADE_EMEC` | texto | Código e-MEC da instituição de ensino superior | `NI` aparece em alguns registros (amostra de cursos de 2013) | todos |
| `sg_entidade_ensino` | `SG_ENTIDADE_ENSINO` | texto | Sigla da instituição de ensino superior do programa; em programa em rede, a da instituição principal | — | todos |
| `nm_entidade_ensino` | `NM_ENTIDADE_ENSINO` | texto | Nome da instituição de ensino superior do programa; em programa em rede, o da instituição principal | — | todos |
| `in_rede` | `IN_REDE` | texto | Indica se o programa pertence a uma rede | `SIM`, `NÃO` | todos |
| `sg_entidade_ensino_rede` | `SG_ENTIDADE_ENSINO_REDE` | texto | Siglas das instituições associadas à principal quando o programa é em rede | lista de siglas; `NA` quando não se aplica | todos |
| `cs_status_juridico` | `CS_STATUS_JURIDICO` | texto | Classificação da natureza jurídica da instituição | `FEDERAL`, `ESTADUAL`, `MUNICIPAL`, `PARTICULAR` | todos |
| `ds_dependencia_administrativa` | `DS_DEPENDENCIA_ADMINISTRATIVA` | texto | Dependência administrativa da instituição | `PÚBLICA`, `PRIVADA` | todos |
| `ds_organizacao_academica` | `DS_ORGANIZACAO_ACADEMICA` | texto | Organização acadêmica da instituição (Decreto nº 5.773/2006, segundo a fonte) | por exemplo `UNIVERSIDADE`, `FACULDADE`, `CENTRO UNIVERSITÁRIO` | todos |
| `nm_regiao` | `NM_REGIAO` | texto | Nome da região sede do programa | `NORTE`, `NORDESTE`, `SUDESTE`, `SUL`, `CENTRO-OESTE` | todos |
| `sg_uf_programa` | `SG_UF_PROGRAMA` | texto | Sigla da unidade da federação sede do programa | sigla de 2 letras | todos |
| `nm_municipio_programa_ies` | `NM_MUNICIPIO_PROGRAMA_IES` | texto | Nome do município sede do programa | — | todos |
| `nm_modalidade_programa` | `NM_MODALIDADE_PROGRAMA` | texto | Modalidade do programa: acadêmico ou profissional | `ACADÊMICO`, `PROFISSIONAL` | todos |
| `cd_programa_ies` | `CD_PROGRAMA_IES` | texto | Código do programa na CAPES, gerado a partir do código da instituição; os 8 primeiros dígitos são o `CD_ENTIDADE_CAPES` | 13 caracteres, como `10001018041P7` | todos |
| `nm_programa_ies` | `NM_PROGRAMA_IES` | texto | Nome do programa, informado pela instituição e aprovado pelo Ministério da Educação | — | todos |
| `nm_programa_idioma` | `NM_PROGRAMA_IDIOMA` | texto | Nome do programa em inglês, informado pela instituição | — | todos |
| `nm_grau_programa` | `NM_GRAU_PROGRAMA` | texto | Nível acadêmico do programa | `MESTRADO`, `DOUTORADO`, `MESTRADO/DOUTORADO`, `MESTRADO PROFISSIONAL`, `DOUTORADO PROFISSIONAL`, `MESTRADO PROFISSIONAL/DOUTORADO PROFISSIONAL` | todos |
| `cd_conceito_programa` | `CD_CONCEITO_PROGRAMA` | texto | Nota ou conceito do programa. Segundo a fonte, varia de 3 a 7 para os cursos recomendados/reconhecidos pela CAPES e pelo CNE | amostra de 2024: `1` a `7` e `A` (179 programas); a fonte não explica `A` | todos |
| `ano_inicio_programa` | `ANO_INICIO_PROGRAMA` | texto | Ano de início do programa | ano de 4 dígitos | P1 |
| `an_inicio_programa` | `AN_INICIO_PROGRAMA` | texto | Ano de início do programa | ano de 4 dígitos | P2 |
| `an_inicio_curso` | `AN_INICIO_CURSO` | texto | Ano de início de cada curso do programa. Quando o grau é mestrado/doutorado, concatena os anos de início de cada um; com um só ano, é o do curso do grau existente | `2001/2005` (um ou dois anos separados por barra) | todos |
| `ds_situacao_programa` | `DS_SITUACAO_PROGRAMA` | texto | Situação do programa no ano de referência | `EM FUNCIONAMENTO`, `EM DESATIVACAO` | todos |
| `dt_situacao_programa` | `DT_SITUACAO_PROGRAMA` | texto | Data de início da situação do programa no ano de referência | formato `28AUG2019:00:00:00` | todos |
| `id_add_foto_programa_ies` | `ID_ADD_FOTO_PROGRAMA_IES` | texto | Identificador da "foto" do último envio do programa referente à instituição (a principal, em programa em rede) | identificador numérico | todos |
| `id_add_foto_programa` | `ID_ADD_FOTO_PROGRAMA` | texto | Identificador da "foto" do último envio do programa | identificador numérico | todos |
| `ds_clientela_quadrienal_2017` | `DS_CLIENTELA_QUADRIENAL_2017` | texto | Identificador de participação do programa como grupo de clientela na Avaliação Quadrienal 2017 | `AVALIAÇÃO`, `AVALIAÇÃO PROFs`, `NÃO` (amostra de 2013) | P1 |

## No lake

- Dataset `capes/programas`, particionado por `ano`, um Parquet por arquivo de origem.
- Todas as colunas são texto, inclusive códigos e datas. O CSV é lido em UTF-8 e, se não for UTF-8 válido, em Windows-1252 (todos os arquivos conferidos caíram no segundo caso).
- Os nomes das colunas são só normalizados (minúsculas, sem acento), sem sinônimos: a coluna do ano de início do programa tem um nome em cada era (`ano_inicio_programa` e `an_inicio_programa`).
- A partição `ano` vem da coluna do ano-base (`an_base`) de cada linha; o ano do nome do arquivo só vale quando o arquivo não tem essa coluna, e então ele precisa ser único, senão o arquivo falha na conversão. Se o nome e a coluna divergem, vale a coluna e a conversão avisa. Se dois arquivos cobrem exatamente os mesmos anos, o de conteúdo idêntico é ignorado com aviso e o de conteúdo diferente gera erro; essa checagem vale dentro de uma única execução de conversão.
- O esquema de referência (`programas.schema.json`) tem 34 colunas, gerado de uma conversão de amostras de 2013, 2021 e 2024; nesses anos todos os layouts conferidos estão representados.

## Cuidados de uso

- **A coluna do ano de início muda de nome.** Para uma série de 2013 a 2024, use `coalesce(ano_inicio_programa, an_inicio_programa)`. Evidência: esquemas de 2013 e 2021 (2026-11-09, versão 0.3.0).
- **Um programa aparece em todos os anos em que existiu.** Para contar programas, filtre por um ano; somar linhas de vários anos conta o mesmo programa várias vezes.
- **Programas em rede.** O programa conta sob a instituição principal; `sg_entidade_ensino_rede` lista as demais. Em 2024, 157 dos 4.635 programas são em rede (`in_rede = SIM`).
- **Conceito.** A fonte diz que a nota varia de 3 a 7, mas a amostra de 2024 traz também `1`, `2` e `A`. Não foi achada definição oficial de `A`.
- **Datas em texto no formato `28AUG2019:00:00:00`.** Converta com `str.strptime` usando o formato `%d%b%Y:%H:%M:%S` e meses em inglês.
- **`cd_entidade_emec` pode vir `NI`.** Não use como número.
- **Chave.** `cd_programa_ies` é único por ano nas amostras de 2013, 2021 e 2024 (3.568, 4.709 e 4.635 linhas, uma por código).
- **Retificações.** A fonte avisa que os programas podem retificar informações depois do envio, e o pacote 2017 a 2020 declara que os dados de 2017 a 2019 foram substituídos com a reabertura do calendário de envio; a versão coletada de cada ano pode mudar.

## Exemplos

Programas por região e modalidade no ano de 2024:

```python
import polars as pl

programas = pl.scan_parquet("lake/capes/programas/ano=2024/*.parquet")
resumo = (
    programas.group_by("nm_regiao", "nm_modalidade_programa")
    .agg(pl.len().alias("programas"))
    .sort("nm_regiao", "nm_modalidade_programa")
    .collect()
)
```

Evolução do número de programas por ano, lendo cada ano separadamente (as colunas mudam entre as eras):

```python
from pathlib import Path

evolucao = pl.DataFrame(
    {
        "ano": [int(d.name[4:]) for d in sorted(Path("lake/capes/programas").glob("ano=[0-9]*"))],
        "programas": [
            pl.scan_parquet(d / "*.parquet").select(pl.col("cd_programa_ies").n_unique()).collect().item()
            for d in sorted(Path("lake/capes/programas").glob("ano=[0-9]*"))
        ],
    }
)
```

## Referências

- Pacote 2021 a 2024: https://dadosabertos.capes.gov.br/dataset/2021-a-2024-programas-da-pos-graduacao-stricto-sensu-no-brasil
- Pacote 2017 a 2020: https://dadosabertos.capes.gov.br/dataset/2017-a-2020-programas-da-pos-graduacao-stricto-sensu-no-brasil
- Pacote 2013 a 2016: https://dadosabertos.capes.gov.br/dataset/programas-da-pos-graduacao-stricto-census-do-brasil-de-2013-a-2015
- Metadados (dicionário de variáveis): https://metadados.capes.gov.br/index.php/catalog/345 (2021 a 2024), https://metadados.capes.gov.br/index.php/catalog/230 (2017 a 2020) e https://metadados.capes.gov.br/index.php/catalog/117 (2013 a 2016)
