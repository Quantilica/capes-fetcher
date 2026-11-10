---
dataset:
  id: cursos
  fonte: capes
  titulo: Cursos de pós-graduação stricto sensu
  resumo: Cursos (mestrado, doutorado e variantes profissionais) dos programas de pós-graduação stricto sensu do Brasil por ano-base, com programa, instituição, localização, área, conceito e situação.
  orgao: Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES)
  pagina_oficial: https://dadosabertos.capes.gov.br/dataset/2021-a-2024-cursos-da-pos-graduacao-stricto-sensu-no-brasil
  licenca: "Creative Commons Attribution (CC BY), conforme os pacotes de cursos no portal de dados abertos da CAPES: http://www.opendefinition.org/licenses/cc-by"
  periodicidade: anual, com atualização em geral no primeiro semestre de cada ano, segundo o metadado oficial
  cobertura: {inicio: "2013", fim: em-curso}
  unidade: um curso de pós-graduação stricto sensu em um ano-base
  granularidade: {espacial: município sede do programa (com UF e região), temporal: ano-base}
  formato_bruto: "CSV por ano-base, separador ponto e vírgula, texto em Windows-1252 (nenhum arquivo conferido é UTF-8), uma linha de cabeçalho"
  lake: {estado: convertido, particoes: [ano], chave: [ano, cd_curso_ppg], colunas: 28}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-09
  versao_fetcher: 0.3.0
---

# Cursos de pós-graduação stricto sensu

## Resumo

Cadastro anual dos cursos que compõem os programas de pós-graduação stricto sensu: cada programa tem um ou mais cursos (mestrado, doutorado, mestrado profissional, doutorado profissional). Traz o código e o nome do curso, o grau, o conceito, o ano de início previsto e a situação, mais os dados do programa e da instituição. A CAPES o produz a partir da coleta na Plataforma Sucupira. Serve para contar cursos por grau, região e área.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `capes/cursos` |
| Órgão | Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) |
| Página oficial | https://dadosabertos.capes.gov.br/dataset/2021-a-2024-cursos-da-pos-graduacao-stricto-sensu-no-brasil |
| Licença | Creative Commons Attribution (CC BY), conforme os pacotes de cursos no portal de dados abertos da CAPES: http://www.opendefinition.org/licenses/cc-by |
| Periodicidade | anual, com atualização em geral no primeiro semestre de cada ano, segundo o metadado oficial |
| Cobertura | 2013 a em-curso |
| Unidade (uma linha) | um curso de pós-graduação stricto sensu em um ano-base |
| Granularidade | espacial: município sede do programa (com UF e região); temporal: ano-base |
| Formato bruto | CSV por ano-base, separador ponto e vírgula, texto em Windows-1252 (nenhum arquivo conferido é UTF-8), uma linha de cabeçalho |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `ano`, `cd_curso_ppg` |
| Colunas | 28 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-09 |
| Versão do fetcher | 0.3.0 |

## Origem e coleta

- O fetcher baixa os CSVs dos pacotes "Cursos da Pós-Graduação Stricto Sensu do Brasil" do portal de dados abertos da CAPES: 2013 a 2016, 2017 a 2020 e 2021 a 2024. Cada pacote traz um CSV e um XLSX por ano-base; o fetcher usa o CSV.
- No bruto, cada ano é `cursos_<AAAA>@<AAAAMMDD>.csv`, em que o sufixo é a data da última modificação do arquivo na fonte (`Last-Modified`), ou, sem ela, a data do CKAN.
- Conferido em 2026-11-09 pela listagem do bruto: 10 arquivos, com os anos 2013, 2015, 2017 a 2024. Faltam 2014 e 2016, e o arquivo `cursos_2013` tem exatamente o mesmo conteúdo (mesmo SHA-256) que `cursos_2015`, com ano-base 2015 (veja os cuidados de uso).

## Conteúdo

- Unidade de análise: um curso, identificado por `cd_curso_ppg`, em um ano-base.
- Cobertura anunciada pela fonte: 2013 a 2024. Número de cursos, pelo metadado oficial: 7.029 em 2022, 7.299 em 2023 e 7.488 em 2024. Nos arquivos de 2021 e 2024 as linhas são 7.161 e 7.488 (a de 2024 confere com o oficial).
- Cada linha é uma "foto" do curso na última imagem homologada do programa, segundo a fonte.
- Layout: o mesmo cabeçalho de 28 colunas em todos os arquivos conferidos (2013 a 2024); não há quebra de layout.

## Variáveis

Descrições dos metadados oficiais da CAPES (versão 2021 a 2024); onde a fonte não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ano` | `AN_BASE` (valor da coluna) | inteiro (partição) | Ano da partição, tirado do ano-base de cada linha (`an_base`); o ano do nome do arquivo só vale se o arquivo não tiver essa coluna. Linha sem ano válido vai para a partição de quarentena (ano nulo) | ano de 4 dígitos | todo |
| `an_base` | `AN_BASE` | texto | Ano de referência das atividades declaradas pelo programa | ano de 4 dígitos | todo |
| `nm_grande_area_conhecimento` | `NM_GRANDE_AREA_CONHECIMENTO` | texto | Nome da grande área de conhecimento do programa do curso | 9 valores | todo |
| `nm_area_conhecimento` | `NM_AREA_CONHECIMENTO` | texto | Nome da área de conhecimento do programa do curso | — | todo |
| `nm_subarea_conhecimento` | `NM_SUBAREA_CONHECIMENTO` | texto | Nome da subárea de conhecimento do programa do curso | `NÃO SE APLICA` quando não se aplica | todo |
| `nm_especialidade` | `NM_ESPECIALIDADE` | texto | Nome da especialidade do conhecimento do programa do curso | `NÃO SE APLICA` quando não se aplica | todo |
| `cd_area_avaliacao` | `CD_AREA_AVALIACAO` | texto | Código identificador da área de avaliação do programa | número, como texto | todo |
| `nm_area_avaliacao` | `NM_AREA_AVALIACAO` | texto | Nome da área de avaliação do programa | — | todo |
| `cd_entidade_capes` | `CD_ENTIDADE_CAPES` | texto | Código da instituição de ensino superior na CAPES | 8 dígitos | todo |
| `cd_entidade_emec` | `CD_ENTIDADE_EMEC` | texto | Código e-MEC da instituição de ensino superior | pode vir `NI` (amostra de 2013) | todo |
| `sg_entidade_ensino` | `SG_ENTIDADE_ENSINO` | texto | Sigla da instituição de ensino superior do programa | — | todo |
| `nm_entidade_ensino` | `NM_ENTIDADE_ENSINO` | texto | Nome da instituição de ensino superior do programa | — | todo |
| `cs_status_juridico` | `CS_STATUS_JURIDICO` | texto | Classificação da natureza jurídica da instituição | `FEDERAL`, `ESTADUAL`, `MUNICIPAL`, `PARTICULAR` | todo |
| `ds_dependencia_administrativa` | `DS_DEPENDENCIA_ADMINISTRATIVA` | texto | Dependência administrativa da instituição | `PÚBLICA`, `PRIVADA` | todo |
| `ds_organizacao_academica` | `DS_ORGANIZACAO_ACADEMICA` | texto | Organização acadêmica da instituição | por exemplo `UNIVERSIDADE`, `NÃO INFORMADO` | todo |
| `nm_regiao` | `NM_REGIAO` | texto | Nome da região sede do programa | `NORTE`, `NORDESTE`, `SUDESTE`, `SUL`, `CENTRO-OESTE` | todo |
| `sg_uf_programa` | `SG_UF_PROGRAMA` | texto | Sigla da unidade da federação sede do programa | sigla de 2 letras | todo |
| `nm_municipio_programa_ies` | `NM_MUNICIPIO_PROGRAMA_IES` | texto | Nome do município sede do programa | — | todo |
| `cd_programa_ies` | `CD_PROGRAMA_IES` | texto | Código do programa do curso na CAPES (13 caracteres; os 8 primeiros são o código da instituição) | como `33004064077P2` | todo |
| `nm_programa_ies` | `NM_PROGRAMA_IES` | texto | Nome do programa do curso | — | todo |
| `cd_curso_ppg` | `CD_CURSO_PPG` | texto | Código do curso de pós-graduação na CAPES | 13 caracteres, como `33004064077D3` | todo |
| `nm_curso` | `NM_CURSO` | texto | Nome do curso de pós-graduação | — | todo |
| `nm_grau_curso` | `NM_GRAU_CURSO` | texto | Nome do grau acadêmico do curso | `MESTRADO`, `DOUTORADO`, `MESTRADO PROFISSIONAL`, `DOUTORADO PROFISSIONAL` | todo |
| `cd_conceito_curso` | `CD_CONCEITO_CURSO` | texto | Nota ou conceito do curso. Segundo a fonte, varia de 3 a 7 para os cursos recomendados/reconhecidos pela CAPES e pelo CNE | amostra de 2024: `1` a `7` e `A` (184 cursos); a fonte não explica `A` | todo |
| `an_inicio_previsto` | `AN_INICIO_PREVISTO` | texto | Ano previsto para o início das atividades do curso. Em cursos `EM PROJETO` sem ano informado, a fonte diz que a variável recebe o valor `9999` | ano de 4 dígitos; `9999` = não informado | todo |
| `ds_situacao_curso` | `DS_SITUACAO_CURSO` | texto | Situação do curso no ano de referência | `EM FUNCIONAMENTO`, `EM PROJETO`, `EM DESATIVACAO` | todo |
| `dt_situacao_curso` | `DT_SITUACAO_CURSO` | texto | Data de início da situação do curso no ano de referência | formato `18SEP2012:00:00:00` | todo |
| `id_add_foto_programa_ies` | `ID_ADD_FOTO_PROGRAMA_IES` | texto | Identificador da "foto" do último envio do programa referente à instituição (a principal, em programa em rede) | identificador numérico | todo |
| `id_add_foto_programa` | `ID_ADD_FOTO_PROGRAMA` | texto | Identificador da "foto" do último envio do programa | identificador numérico | todo |

## No lake

- Dataset `capes/cursos`, particionado por `ano`, um Parquet por arquivo de origem.
- Todas as colunas são texto. O CSV é lido em UTF-8 e, se não for UTF-8 válido, em Windows-1252 (todos os arquivos conferidos caíram no segundo caso). Nomes de coluna só normalizados (minúsculas, sem acento), sem sinônimos.
- A partição `ano` vem da coluna do ano-base (`an_base`) de cada linha; o ano do nome do arquivo só vale quando o arquivo não tem essa coluna, e então ele precisa ser único, senão o arquivo falha na conversão. Se o nome e a coluna divergem, vale a coluna e a conversão avisa. Se dois arquivos cobrem exatamente os mesmos anos, o de conteúdo idêntico é ignorado com aviso e o de conteúdo diferente gera erro; essa checagem vale dentro de uma única execução de conversão.
- O esquema de referência (`cursos.schema.json`) tem 28 colunas, gerado de uma conversão de amostras de 2013, 2021 e 2024.

## Cuidados de uso

- **O arquivo `cursos_2013` contém dados de 2015.** O bruto conferido tem `cursos_2013@20230126.csv` e `cursos_2015@20230126.csv` com o mesmo SHA-256, e a coluna `an_base` vale `2015` em ambos. Como a partição vem de `an_base` e o conteúdo é idêntico, o lake tem `ano=2015` uma vez (6.060 linhas, de 3.946 programas distintos, o mesmo número que o metadado oficial dá para 2015) e não tem `ano=2013`; o segundo arquivo é ignorado com aviso. Faltam no bruto os anos-base 2013, 2014 e 2016, portanto não há dados de cursos desses anos.
- **Reconversão de um lake antigo.** Um lake convertido antes desta regra tem `ano=2013` com dados de 2015 e, se a conversão foi refeita por cima, linhas duplicadas; apague `capes/cursos` do lake antes de converter de novo.
- **`ano` e `an_base`** coincidem no lake atual, porque a partição vem de `an_base`; a divergência só existe no nome do arquivo bruto.
- **`an_inicio_previsto = 9999`** significa ano não informado em cursos em projeto, segundo a fonte (máximo encontrado na amostra de 2024: 9999; mínimo: 1931). Descarte antes de calcular idades.
- **Conceito.** Além de 3 a 7, a amostra de 2024 traz `1`, `2` e `A`. Não foi achada definição oficial de `A`.
- **Cursos em projeto.** `ds_situacao_curso = EM PROJETO` (242 cursos em 2024) são cursos ainda não iniciados; exclua-os para contar cursos em funcionamento.
- **Data da situação concentrada.** Na amostra de 2024, 2.533 de 7.488 cursos têm `dt_situacao_curso = 18SEP2012:00:00:00`; a fonte só diz que é a data de início da situação, por isso não a use como data de criação do curso.
- **Chave.** `cd_curso_ppg` é único por arquivo nas amostras de 2013, 2021 e 2024.

## Exemplos

Cursos em funcionamento em 2024, por grau e região:

```python
import polars as pl

cursos = pl.scan_parquet("lake/capes/cursos/ano=2024/*.parquet")
resumo = (
    cursos.filter(
        (pl.col("an_base") == "2024") & (pl.col("ds_situacao_curso") == "EM FUNCIONAMENTO")
    )
    .group_by("nm_regiao", "nm_grau_curso")
    .agg(pl.len().alias("cursos"))
    .sort("nm_regiao", "nm_grau_curso")
    .collect()
)
```

## Referências

- Pacote 2021 a 2024: https://dadosabertos.capes.gov.br/dataset/2021-a-2024-cursos-da-pos-graduacao-stricto-sensu-no-brasil
- Pacote 2017 a 2020: https://dadosabertos.capes.gov.br/dataset/2017-a-2020-cursos-da-pos-graduacao-stricto-sensu-no-brasil
- Pacote 2013 a 2016: https://dadosabertos.capes.gov.br/dataset/cursos-da-pos-graduacao-stricto-sensu-do-brasil-de-2013-a-2015
- Metadados (dicionário de variáveis): https://metadados.capes.gov.br/index.php/catalog/339 (2021 a 2024), https://metadados.capes.gov.br/index.php/catalog/231 (2017 a 2020) e https://metadados.capes.gov.br/index.php/catalog/116 (2013 a 2016)
