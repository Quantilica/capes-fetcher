# CAPES — pós-graduação (`capes`)

O `capes-fetcher` coleta dados abertos da Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES), fundação do Ministério da Educação, a partir do portal de dados abertos da instituição (CKAN). Hoje converte para o lake em Parquet particionado três conjuntos sobre a pós-graduação stricto sensu brasileira, todos extraídos da Plataforma Sucupira: o catálogo de teses e dissertações, os programas e os cursos.

| Dataset | O que é | Origem | Período | Página |
|---|---|---|---|---|
| `teses` | Catálogo de Teses e Dissertações: uma linha por trabalho de conclusão defendido em programa de pós-graduação | Pacotes "Catálogo de Teses e Dissertações - Brasil" do portal de dados abertos | 1987 a 2024 | [teses](datasets/teses.md) |
| `programas` | Programas de pós-graduação stricto sensu por ano-base: instituição, área, conceito, situação | Pacotes "Programas da Pós-Graduação Stricto Sensu" | 2013 a 2024 | [programas](datasets/programas.md) |
| `cursos` | Cursos (mestrado, doutorado e variantes profissionais) dos programas, por ano-base | Pacotes "Cursos da Pós-Graduação Stricto Sensu" | 2013 a 2024 (veja os cuidados de uso) | [cursos](datasets/cursos.md) |

## Como a CAPES publica

- O portal `dadosabertos.capes.gov.br` organiza os dados em pacotes por tema e por intervalo de anos (por exemplo, "[2021 a 2024] Catálogo de Teses e Dissertações - Brasil"). Cada pacote traz um CSV e um XLSX por ano-base, mais um PDF e uma página de metadados no catálogo `metadados.capes.gov.br`.
- Os três conjuntos têm periodicidade anual, segundo o portal; o documento de metadados diz que a atualização ocorre, em geral, no primeiro semestre de cada ano, e que pode haver reenvio de anos anteriores quando o calendário de coleta é reaberto.
- Licença declarada em todos os pacotes: Creative Commons Attribution (CC BY), http://www.opendefinition.org/licenses/cc-by.
- Os dados vêm da coleta feita pelos programas na Plataforma Sucupira. Segundo a CAPES, só a última imagem homologada de cada programa vale para a avaliação, e programas podem retificar informações depois do envio.
- Os CSVs são separados por `;` e, nos arquivos conferidos, não estão em UTF-8; o conversor os lê em Windows-1252.

O fetcher guarda cada versão baixada com a data de coleta no nome do arquivo (`<arquivo>@AAAAMMDD`); o lake converte a versão mais recente de cada arquivo.

## Como os conjuntos se relacionam

- `programas`, `cursos` e `teses` compartilham o código do programa: `cd_programa_ies` (programas e cursos) é o mesmo código que `codigo_programa` em `teses`, com 13 caracteres, cujos 8 primeiros dígitos correspondem ao código da instituição na CAPES (`cd_entidade_capes`), segundo a documentação da CAPES. Numa amostra de 2024, os 126 programas presentes em `teses` constam todos em `programas`, e os 4.635 programas de `cursos` constam todos em `programas`.
- Um programa tem um ou mais cursos (mestrado, doutorado); uma tese ou dissertação pertence a um programa.
- Os pacotes da CAPES cobrem outros temas (bolsas, produção intelectual, docentes, periódicos, entre outros) que o fetcher cataloga, mas ainda não baixa nem converte.

## Quebras que valem para mais de um conjunto

| Desde | Mudança | Afeta |
|---|---|---|
| 2013 | Os dados passam a vir da Plataforma Sucupira; o layout dos arquivos muda (nomes de coluna em `AN_BASE`, `CD_PROGRAMA` etc.) | `teses`, `programas`, `cursos` |
| 2017 | Os programas ganham a coluna `NM_AREA_BASICA` e perdem a coluna de clientela da Avaliação Quadrienal 2017; `ANO_INICIO_PROGRAMA` passa a `AN_INICIO_PROGRAMA` | `programas` |

Os nomes de coluna e os formatos de data variam entre esses grupos de anos; as páginas de cada dataset listam as colunas por período.
