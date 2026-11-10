---
dataset:
  id: teses
  fonte: capes
  titulo: Catálogo de Teses e Dissertações
  resumo: Teses, dissertações e outros trabalhos de conclusão de cursos de pós-graduação stricto sensu defendidos no Brasil, um por linha, com instituição, programa, área, autor, orientador e data de defesa.
  orgao: Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES)
  pagina_oficial: https://dadosabertos.capes.gov.br/dataset/2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil
  licenca: "Creative Commons Attribution (CC BY), conforme os pacotes do catálogo no portal de dados abertos da CAPES: http://www.opendefinition.org/licenses/cc-by"
  periodicidade: anual, com atualização em geral no primeiro semestre de cada ano, segundo o metadado oficial
  cobertura: {inicio: "1987", fim: em-curso}
  unidade: um trabalho de conclusão (tese, dissertação ou outro) de um discente de pós-graduação stricto sensu
  granularidade: {espacial: instituição de ensino e programa (com região e UF da instituição), temporal: ano-base e data de defesa}
  formato_bruto: "CSV por ano-base, separador ponto e vírgula, texto em Windows-1252 (nenhum arquivo conferido é UTF-8), uma linha de cabeçalho; três layouts de colunas conforme o período"
  lake: {estado: convertido, particoes: [ano], chave: [], colunas: 86}
  unidades_de_medida:
    numeropaginas: páginas
    nr_paginas: páginas
    volume: volumes
    nr_volume: volumes
  dados_pessoais:
    - {coluna: autor, categoria: nome}
    - {coluna: documento_discente, categoria: "CPF do discente, parcialmente mascarado pela fonte"}
    - {coluna: id_pessoa_discente, categoria: "identificador da pessoa na base da CAPES, vinculado ao CPF"}
    - {coluna: orientador, categoria: nome}
    - {coluna: orientador_2, categoria: nome}
    - {coluna: orientador_3, categoria: nome}
    - {coluna: orientador_4, categoria: nome}
    - {coluna: coorientador, categoria: nome}
    - {coluna: coorientador_2, categoria: nome}
    - {coluna: coorientador_3, categoria: nome}
    - {coluna: coorientador_4, categoria: nome}
    - {coluna: documentoorientador_1, categoria: "CPF do orientador, parcialmente mascarado pela fonte"}
    - {coluna: documentoorientador_2, categoria: "CPF do orientador, parcialmente mascarado pela fonte"}
    - {coluna: documentoorientador_3, categoria: "CPF do orientador, parcialmente mascarado pela fonte"}
    - {coluna: documentoorientador_4, categoria: "CPF do orientador, parcialmente mascarado pela fonte"}
    - {coluna: documentocoorientador_1, categoria: "CPF do coorientador, parcialmente mascarado pela fonte"}
    - {coluna: documentocoorientador_2, categoria: "CPF do coorientador, parcialmente mascarado pela fonte"}
    - {coluna: documentocoorientador_3, categoria: "CPF do coorientador, parcialmente mascarado pela fonte"}
    - {coluna: documentocoorientador_4, categoria: "CPF do coorientador, parcialmente mascarado pela fonte"}
    - {coluna: id_pessoa_orientador, categoria: "identificador da pessoa na base da CAPES, vinculado ao CPF"}
    - {coluna: nm_tp_vinculo, categoria: "tipo de vínculo empregatício atual do discente"}
    - {coluna: dt_matricula, categoria: "data de matrícula do discente"}
  eras:
    - {desde: "1987-01", mudanca: "Layout A (41 colunas): nomes em CamelCase (AnoBase, TituloTese, Nivel), com CPF mascarado de discente e de orientadores; data no formato dd/mm/aaaa"}
    - {desde: "2013-01", mudanca: "Layout B (56 colunas lidas pelo conversor): nomes em maiúsculas com sublinhado (AN_BASE, NM_PRODUCAO), identificadores de produção, área de concentração, linha e projeto, e dados do discente e do orientador (vínculo, expectativa de atuação); datas dd/mm/aaaa hh:mm:ss"}
    - {desde: "2017-01", mudanca: "Layout C (59 colunas): acrescenta o código da instituição (CD_ENTIDADE_CAPES) e o vínculo do trabalho com produção intelectual; datas no formato ddMMMaaaa:hh:mm:ss, como 27MAR2024:00:00:00. Nos arquivos conferidos o layout C aparece de 2018 em diante; o ano de 2017 não consta no bruto"}
  revisado_em: 2026-11-09
  versao_fetcher: 0.3.0
---

# Catálogo de Teses e Dissertações

## Resumo

Registro das teses, dissertações e outros trabalhos de conclusão dos cursos de pós-graduação stricto sensu do país, com a instituição e o programa, a área de conhecimento e de avaliação, o autor, o orientador, a data de defesa, o resumo e as palavras-chave. A CAPES o alimenta a partir da coleta dos programas na Plataforma Sucupira. Serve para estudar a produção acadêmica por instituição, área, região e ano.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `capes/teses` |
| Órgão | Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) |
| Página oficial | https://dadosabertos.capes.gov.br/dataset/2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil |
| Licença | Creative Commons Attribution (CC BY), conforme os pacotes do catálogo no portal de dados abertos da CAPES: http://www.opendefinition.org/licenses/cc-by |
| Periodicidade | anual, com atualização em geral no primeiro semestre de cada ano, segundo o metadado oficial |
| Cobertura | 1987 a em-curso |
| Unidade (uma linha) | um trabalho de conclusão (tese, dissertação ou outro) de um discente de pós-graduação stricto sensu |
| Granularidade | espacial: instituição de ensino e programa (com região e UF da instituição); temporal: ano-base e data de defesa |
| Formato bruto | CSV por ano-base, separador ponto e vírgula, texto em Windows-1252 (nenhum arquivo conferido é UTF-8), uma linha de cabeçalho; três layouts de colunas conforme o período |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | — |
| Colunas | 86 |
| Unidades de medida | `numeropaginas`: páginas; `nr_paginas`: páginas; `volume`: volumes; `nr_volume`: volumes |
| Dados pessoais | `autor` (nome); `documento_discente` (CPF do discente, parcialmente mascarado pela fonte); `id_pessoa_discente` (identificador da pessoa na base da CAPES, vinculado ao CPF); `orientador` (nome); `orientador_2` (nome); `orientador_3` (nome); `orientador_4` (nome); `coorientador` (nome); `coorientador_2` (nome); `coorientador_3` (nome); `coorientador_4` (nome); `documentoorientador_1` (CPF do orientador, parcialmente mascarado pela fonte); `documentoorientador_2` (CPF do orientador, parcialmente mascarado pela fonte); `documentoorientador_3` (CPF do orientador, parcialmente mascarado pela fonte); `documentoorientador_4` (CPF do orientador, parcialmente mascarado pela fonte); `documentocoorientador_1` (CPF do coorientador, parcialmente mascarado pela fonte); `documentocoorientador_2` (CPF do coorientador, parcialmente mascarado pela fonte); `documentocoorientador_3` (CPF do coorientador, parcialmente mascarado pela fonte); `documentocoorientador_4` (CPF do coorientador, parcialmente mascarado pela fonte); `id_pessoa_orientador` (identificador da pessoa na base da CAPES, vinculado ao CPF); `nm_tp_vinculo` (tipo de vínculo empregatício atual do discente); `dt_matricula` (data de matrícula do discente) |
| Eras | 1987-01: Layout A (41 colunas): nomes em CamelCase (AnoBase, TituloTese, Nivel), com CPF mascarado de discente e de orientadores; data no formato dd/mm/aaaa; 2013-01: Layout B (56 colunas lidas pelo conversor): nomes em maiúsculas com sublinhado (AN_BASE, NM_PRODUCAO), identificadores de produção, área de concentração, linha e projeto, e dados do discente e do orientador (vínculo, expectativa de atuação); datas dd/mm/aaaa hh:mm:ss; 2017-01: Layout C (59 colunas): acrescenta o código da instituição (CD_ENTIDADE_CAPES) e o vínculo do trabalho com produção intelectual; datas no formato ddMMMaaaa:hh:mm:ss, como 27MAR2024:00:00:00. Nos arquivos conferidos o layout C aparece de 2018 em diante; o ano de 2017 não consta no bruto |
| Revisado em | 2026-11-09 |
| Versão do fetcher | 0.3.0 |

## Origem e coleta

- O fetcher baixa os arquivos CSV dos pacotes "Catálogo de Teses e Dissertações - Brasil" do portal de dados abertos da CAPES: 1987 a 2012, 2013 a 2016, 2017 a 2020 e 2021 a 2024. Cada pacote traz um CSV e um XLSX por ano-base; o fetcher usa o CSV.
- No bruto, cada ano é `teses_<AAAA>@<AAAAMMDD>.csv`, em que o sufixo é a data da última modificação do arquivo na fonte (`Last-Modified`), ou, sem ela, a data do CKAN.
- Conferido em 2026-11-09 pela listagem do bruto: 36 arquivos, de 1987 a 2024, sem os anos 2017 e 2021. Os pacotes da CAPES anunciam esses dois anos; o bruto conferido não os tem.
- A conversão também aceita CSVs dentro de um ZIP. Documentação, provas e arquivos temporários não são convertidos: só entram arquivos CSV cujo nome contenha `tese`, `dissertacao`, `btd` ou `dados_` (e não `programa` nem `curso`).

## Conteúdo

- Unidade de análise: um trabalho de conclusão. Os metadados oficiais descrevem o universo como "discentes de pós-graduação no Brasil" e a unidade como "produto".
- Cobertura anunciada pela fonte: 1987 a 2024, em quatro pacotes (1987 a 2012, 2013 a 2016, 2017 a 2020, 2021 a 2024). O pacote mais recente tem metadado de 2025-12-01.
- Volume anunciado pelo metadado oficial: 82.690 trabalhos em 2021, 84.085 em 2022, 91.463 em 2023 e 91.833 em 2024; 67.534 em 2013. Não foi feita contagem integral dos arquivos (amostra de 2026-11-09).
- Eras (três layouts de colunas):
    - **Layout A, 1987 a 2012:** 41 colunas em CamelCase. Os campos de pessoa vêm com o CPF mascarado.
    - **Layout B, 2013 a 2016:** 56 colunas lidas, a partir da Plataforma Sucupira, com identificadores de produção, de área de concentração, linha de pesquisa e projeto.
    - **Layout C, 2018 em diante nos arquivos conferidos (2017 anunciado pela fonte):** 59 colunas; inclui `codigo_ies`, `in_tcc_com_vinculo_producao` e `id_add_producao_vinculo_ct`.
- Os tipos de trabalho mudam: no layout A só há mestrado, doutorado e profissionalizante; a partir de 2013 existe o subtipo da produção (`nm_subtipo_producao`) e, em 2024, também aparecem formatos como material didático, produto ou processo, projeto técnico e artigo (amostra de 2024).

## Variáveis

Descrições dos metadados oficiais da CAPES (versões 1987 a 2012, 2013 a 2016 e 2021 a 2024 do catálogo); onde a fonte não define a variável, a célula diz "não informado pela fonte". Todos os valores chegam ao lake como texto. A coluna "Período" usa os layouts A (1987 a 2012), B (2013 a 2016) e C (2017 em diante).

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ano` | ano-base (de `AnoBase` ou `AN_BASE`) | inteiro (partição) | Ano-base da coleta; é a partição do dataset. Linha sem ano válido vai para a partição de quarentena (`ano=__HIVE_DEFAULT_PARTITION__`) | ano de 4 dígitos | todos |
| `ano_base` | `AnoBase` (A); `AN_BASE` (B, C) | texto | Ano-base da coleta dos dados | ano de 4 dígitos | todos |
| `codigo_programa` | `CodigoPrograma` (A); `CD_PROGRAMA` (B, C) | texto | Código do programa de pós-graduação na CAPES, gerado a partir do código da instituição; único por programa | 13 caracteres, como `33005010005P4` | todos |
| `regiao` | `Regiao` | texto | Nome da região da instituição | `NORTE`, `NORDESTE`, `SUDESTE`, `SUL`, `CENTRO-OESTE` | A |
| `uf` | `Uf` | texto | Sigla da unidade da federação da instituição | sigla de 2 letras | A |
| `sigla_ies` | `SiglaIes` (A); `SG_ENTIDADE_ENSINO` (B, C) | texto | Sigla da instituição de ensino superior do programa | — | todos |
| `nome_ies` | `NomeIes` (A); `NM_ENTIDADE_ENSINO` (B, C) | texto | Nome da instituição de ensino superior do programa | — | todos |
| `nome_programa` | `NomePrograma` (A); `NM_PROGRAMA` (B, C) | texto | Nome do programa de pós-graduação, informado pela instituição e aprovado pelo Ministério da Educação | — | todos |
| `grandeareacodigo` | `GrandeAreaCodigo` | texto | Código da grande área de conhecimento do programa | código numérico de 8 dígitos | A |
| `grandeareadescricao` | `GrandeAreaDescricao` | texto | Nome da grande área de conhecimento do programa | — | A |
| `areaconhecimentocodigo` | `AreaConhecimentoCodigo` | texto | Código da área de conhecimento do programa | código numérico de 8 dígitos | A |
| `area_conhecimento` | `AreaConhecimento` (A); `NM_AREA_CONHECIMENTO` (B, C) | texto | Nome da área de conhecimento do programa | — | todos |
| `area_avaliacao` | `AreaAvaliacao` (A); `NM_AREA_AVALIACAO` (B, C) | texto | Nome da área de avaliação do programa, na data do envio e homologação | — | todos |
| `documento_discente` | `DocumentoDiscente` | texto | CPF do discente, "tarjado" (parcialmente mascarado) pela fonte | formato `999*****999`; em 1987, 4.492 de 4.496 linhas da amostra têm o valor `999*****999` | A |
| `autor` | `Autor` (A); `NM_DISCENTE` (B, C) | texto | Nome do autor do trabalho (discente) | — | todos |
| `titulo` | `TituloTese` (A); `NM_PRODUCAO` (B, C) | texto | Título da tese ou dissertação | — | todos |
| `grau_academico` | `Nivel` (A); `NM_GRAU_ACADEMICO` (B, C) | texto | Nível do programa (A) ou grau acadêmico do discente em 31 de dezembro do ano-base (B, C) | A: `Mestrado`, `Doutorado`, `Profissionalizante`; B, C: `MESTRADO`, `DOUTORADO`, `MESTRADO PROFISSIONAL`, `DOUTORADO PROFISSIONAL` | todos |
| `data_defesa` | `DataDefesa` (A); `DT_TITULACAO` (B, C) | texto | Data de defesa, que o metadado oficial define como a data da titulação do autor | A: `dd/mm/aaaa`; B: `dd/mm/aaaa hh:mm:ss`; C: `27MAR2024:00:00:00` | todos |
| `palavras_chave` | `PalavrasChave` (A); `DS_PALAVRA_CHAVE` (B, C) | texto | Palavras-chave da tese ou dissertação | separador varia: espaços repetidos (1987), vírgula (2004, 2013), ponto e vírgula (2020, 2024), conforme as amostras | todos |
| `volume` | `Volume` | texto | Número de volumes impressos, encadernados e depositados na biblioteca depositária | volumes | A |
| `numeropaginas` | `NumeroPaginas` | texto | Número de páginas da produção | páginas | A |
| `bibliotecadepositaria` | `BibliotecaDepositaria` | texto | Descrição da biblioteca depositária | — | A |
| `idioma` | `Idioma` | texto | Idioma da produção | `Português`, `Inglês`, `Outro` (amostra de 2004) | A |
| `resumo` | `ResumoTese` (A); `DS_RESUMO` (B, C) | texto | Resumo da tese ou dissertação, em português nos layouts B e C | — | todos |
| `linhapesquisa` | `LinhaPesquisa` | texto | Descrição da linha de pesquisa | — | A |
| `urltextocompleto` | `URLTextoCompleto` | texto | URL do texto completo da produção | URL; vazio na maioria das linhas das amostras de 1987 e 2004 | A |
| `documentoorientador_1` | `DocumentoOrientador_1` | texto | CPF tarjado do orientador 1 | formato `(004*****897)` | A |
| `orientador` | `Orientador_1` (A); `NM_ORIENTADOR` (B, C) | texto | Nome do orientador (o primeiro, em A) | — | todos |
| `documentoorientador_2` | `DocumentoOrientador_2` | texto | CPF tarjado do orientador 2 | — | A |
| `orientador_2` | `Orientador_2` | texto | Nome do orientador 2 | — | A |
| `documentoorientador_3` | `DocumentoOrientador_3` | texto | CPF tarjado do orientador 3 | — | A |
| `orientador_3` | `Orientador_3` | texto | Nome do orientador 3 | — | A |
| `documentoorientador_4` | `DocumentoOrientador_4` | texto | CPF tarjado do orientador 4 | — | A |
| `orientador_4` | `Orientador_4` | texto | Nome do orientador 4 | — | A |
| `documentocoorientador_1` | `DocumentoCoOrientador_1` | texto | CPF tarjado do coorientador 1 | — | A |
| `coorientador` | `CoOrientador_1` | texto | Nome do coorientador 1 | — | A |
| `documentocoorientador_2` | `DocumentoCoOrientador_2` | texto | CPF tarjado do coorientador 2 | — | A |
| `coorientador_2` | `CoOrientador_2` | texto | Nome do coorientador 2 | — | A |
| `documentocoorientador_3` | `DocumentoCoOrientador_3` | texto | CPF tarjado do coorientador 3 | — | A |
| `coorientador_3` | `CoOrientador_3` | texto | Nome do coorientador 3 | — | A |
| `documentocoorientador_4` | `DocumentoCoOrientador_4` | texto | CPF tarjado do coorientador 4 | — | A |
| `coorientador_4` | `CoOrientador_4` | texto | Nome do coorientador 4 | — | A |
| `id_add_producao_intelectual` | `ID_ADD_PRODUCAO_INTELECTUAL` | texto | Identificação da tese ou dissertação no ano-base e no programa na base da CAPES | identificador numérico | B, C |
| `id_producao_intelectual` | `ID_PRODUCAO_INTELECTUAL` | texto | Identificador da tese ou dissertação na base da CAPES | identificador numérico | B, C |
| `id_subtipo_producao` | `ID_SUBTIPO_PRODUCAO` | texto | Identificador do subtipo da produção. Segundo a fonte, segue o grau acadêmico: tese para doutorado; dissertação para mestrado e mestrado profissional; no mestrado profissional há outras modalidades de trabalho de conclusão | identificador numérico | B, C |
| `nm_subtipo_producao` | `NM_SUBTIPO_PRODUCAO` | texto | Nome do subtipo da produção | 2013: `DISSERTAÇÃO`, `TESE`; 2024: 17 valores, entre eles `MATERIAL DIDÁTICO E INSTRUCIONAL`, `PROJETO TÉCNICO`, `ARTIGO` (amostras) | B, C |
| `id_area_concentracao` | `ID_AREA_CONCENTRACAO` | texto | Identificador da área de concentração do programa a que a produção está vinculada | identificador numérico | B, C |
| `nm_area_concentracao` | `NM_AREA_CONCENTRACAO` | texto | Nome da área de concentração do programa a que a produção está vinculada | pode vir `NÃO INFORMADO` | B, C |
| `id_linha_pesquisa` | `ID_LINHA_PESQUISA` | texto | Identificador da linha de pesquisa do programa a que a produção está vinculada | identificador numérico | B, C |
| `nm_linha_pesquisa` | `NM_LINHA_PESQUISA` | texto | Nome da linha de pesquisa do programa a que a produção está vinculada | — | B, C |
| `id_projeto` | `ID_PROJETO` | texto | Identificador do projeto de pesquisa do programa a que a produção está vinculada | identificador numérico | B, C |
| `nm_projeto` | `NM_PROJETO` | texto | Nome do projeto de pesquisa do programa a que a produção está vinculada | — | B, C |
| `dh_inicio_area_conc` | `DH_INICIO_AREA_CONC` | texto | Data e hora do início da área de concentração do programa | B: vazio na amostra de 2013; C: `01AUG2017:00:00:00` | B, C |
| `dh_fim_area_conc` | `DH_FIM_AREA_CONC` | texto | Data e hora do fim da área de concentração do programa | idem | B, C |
| `dh_inicio_linha` | `DH_INICIO_LINHA` | texto | Data e hora do início da linha de pesquisa do programa | B: `01/01/2012 00:00:00`; C: `10JAN2021:00:00:00` | B, C |
| `dh_fim_linha` | `DH_FIM_LINHA` | texto | Data e hora do fim da linha de pesquisa do programa | idem | B, C |
| `ds_keyword` | `DS_KEYWORD` | texto | Palavras-chave (keywords) da produção, em geral em inglês | — | B, C |
| `in_trabalho_mesma_area` | `IN_TRABALHO_MESMA_AREA` | texto | Segundo a fonte, indica se a expectativa de atuação profissional do concluinte é na mesma área da formação | `0`, `1` | B, C |
| `nm_tp_vinculo` | `NM_TP_VINCULO` | texto | Tipo de vínculo empregatício atual do discente | `NÃO INFORMADO`, `SERVIDOR PÚBLICO`, `CLT`, `COLABORADOR`, `BOLSA DE FIXAÇÃO`, `APOSENTADO` (amostra de 2013) | B, C |
| `in_orient_participou_banca` | `IN_ORIENT_PARTICIPOU_BANCA` | texto | Indica se o orientador participou da banca | `0`, `1` | B, C |
| `ds_biblioteca_depositaria` | `DS_BIBLIOTECA_DEPOSITARIA` | texto | Biblioteca depositária da tese ou dissertação | pode vir `NÃO INFORMADO` | B, C |
| `id_tp_expectativa_atuacao` | `ID_TP_EXPECTATIVA_ATUACAO` | texto | Identificador do tipo de expectativa de atuação | identificador numérico | B, C |
| `nm_expectativa_atuacao` | `NM_EXPECTATIVA_ATUACAO` | texto | Nome da expectativa de atuação do discente | `ENSINO E PESQUISA`, `EMPRESAS`, `PESQUISA`, `PROFISSIONAL AUTÔNOMO`, `OUTROS`, `NÃO INFORMADO` (amostra de 2013) | B, C |
| `id_pessoa_discente` | `ID_PESSOA_DISCENTE` | texto | Identifica o discente como pessoa na base da CAPES, em relação ao cadastro de pessoa física da Receita Federal; único independentemente do vínculo, grau e programa | identificador numérico | B, C |
| `dt_matricula` | `DT_MATRICULA` | texto | Data de matrícula do discente no programa | B: `01/03/2010 00:00:00`; C: `18APR2022:00:00:00` | B, C |
| `id_grau_academico` | `ID_GRAU_ACADEMICO` | texto | Identificador do grau acadêmico do discente em 31 de dezembro do ano-base | identificador numérico | B, C |
| `ds_categoria_orientador` | `DS_CATEGORIA_ORIENTADOR` | texto | Categoria do orientador no programa | `DOCENTE`, `PARTICIPANTE EXTERNO`, `NÃO INFORMADO` (amostra de 2013) | B, C |
| `nm_categoria_docente` | `NM_CATEGORIA_DOCENTE` | texto | Categoria do docente, quando o orientador é docente do programa; do contrário, segundo a fonte, fica `NÃO INFORMADO` | `PERMANENTE`, `COLABORADOR`, `VISITANTE`, `NÃO INFORMADO` | B, C |
| `nm_regiao` | `NM_REGIAO` | texto | Nome da região da instituição | `NORTE`, `NORDESTE`, `SUDESTE`, `SUL`, `CENTRO-OESTE` | B, C |
| `sg_uf_ies` | `SG_UF_IES` | texto | Sigla da unidade da federação da instituição | sigla de 2 letras | B, C |
| `nm_uf_ies` | `NM_UF_IES` | texto | Nome da unidade da federação da instituição | — | B, C |
| `cd_grande_area_conhecimento` | `CD_GRANDE_AREA_CONHECIMENTO` | texto | Código da grande área de conhecimento do programa | código de 8 dígitos | B, C |
| `grande_area` | `NM_GRANDE_AREA_CONHECIMENTO` | texto | Nome da grande área de conhecimento do programa | — | B, C |
| `cd_area_conhecimento` | `CD_AREA_CONHECIMENTO` | texto | Código da área de conhecimento do programa | código de 8 dígitos | B, C |
| `cd_subarea_conhecimento` | `CD_SUBAREA_CONHECIMENTO` | texto | Código da subárea de conhecimento do programa | código de 8 dígitos; `NA` quando não se aplica | B, C |
| `nm_subarea_conhecimento` | `NM_SUBAREA_CONHECIMENTO` | texto | Nome da subárea de conhecimento do programa | `NÃO SE APLICA` quando não se aplica | B, C |
| `cd_especialidade` | `CD_ESPECIALIDADE` | texto | Código da especialidade de conhecimento do programa | `NA` quando não se aplica | B, C |
| `nm_especialidade` | `NM_ESPECIALIDADE` | texto | Nome da especialidade de conhecimento do programa | `NÃO SE APLICA` quando não se aplica | B, C |
| `nr_volume` | `NR_VOLUME` | texto | Número de volumes impressos, encadernados e depositados na biblioteca depositária | volumes | B, C |
| `nr_paginas` | `NR_PAGINAS` | texto | Número de páginas da produção | páginas; o valor `0` aparece com frequência (veja os cuidados de uso) | B, C |
| `nm_idioma` | `NM_IDIOMA` | texto | Idioma da produção | `PORTUGUES`, `INGLES`, `ESPANHOL` e outros, sem acento | B, C |
| `abstract` | `DS_ABSTRACT` | texto | Abstract da produção, em inglês | — | B, C |
| `url_texto_completo` | `DS_URL_TEXTO_COMPLETO` | texto | URL do texto completo da produção; nas amostras de 2013 a 2024 todas as linhas trazem um endereço de consulta na Plataforma Sucupira | URL | B, C |
| `id_pessoa_orientador` | `ID_PESSOA_ORIENTADOR` | texto | Identifica o orientador vinculado à produção como pessoa na base da CAPES, em relação ao cadastro de pessoa física da Receita Federal | identificador numérico | B, C |
| `codigo_ies` | `CD_ENTIDADE_CAPES` | texto | Código da instituição de ensino superior na CAPES | 8 dígitos | C |
| `in_tcc_com_vinculo_producao` | `IN_TCC_COM_VINCULO_PRODUCAO` | texto | Indica se o trabalho de conclusão tem vínculo com alguma produção intelectual | `SIM`; vazio quando não há vínculo (amostra de 2024) | C |
| `id_add_producao_vinculo_ct` | `ID_ADD_PRODUCAO_VINCULO_CT` | texto | Identificadores das produções intelectuais vinculadas ao trabalho, concatenados | lista de identificadores | C |

## No lake

- Dataset `capes/teses`, particionado por `ano`, um conjunto de Parquet por arquivo de origem.
- Todas as colunas são texto, inclusive códigos (sem perda de zeros à esquerda) e datas. O esquema não depende do conteúdo lido.
- O CSV é lido em UTF-8 e, se não for UTF-8 válido, em Windows-1252; bytes indefinidos viram o caractere de controle de mesmo código, sem perda.
- Nomes de coluna em minúsculas sem acento; um dicionário de sinônimos leva nomes dos três layouts para nomes comuns (por exemplo `TituloTese`, `NM_PRODUCAO` e `DS_TITULO` viram `titulo`; `Nivel` e `NM_GRAU_ACADEMICO` viram `grau_academico`; `CD_ENTIDADE_CAPES` vira `codigo_ies`). Nomes sem sinônimo ficam só normalizados: por isso há colunas coladas (`grandeareadescricao`, `numeropaginas`, `linhapesquisa`) no layout A e `nm_*`/`cd_*` nos layouts B e C.
- Quando duas colunas de um arquivo apontam para o mesmo nome comum, só uma recebe o nome comum; a outra mantém o nome normalizado. Os campos `DS_RESUMO` (português) e `DS_ABSTRACT` (inglês) dos layouts B e C são colunas separadas: `resumo` e `abstract`. No layout A (1987 a 2012) só há `resumo` (de `ResumoTese`) e não há `abstract`.
- A partição `ano` vem da coluna do ano-base de cada linha (primeiro número de 4 dígitos entre 1900 e 2100); linha sem ano válido vai para a partição de quarentena, sem ano inventado.
- Colunas que existem só em alguns layouts aparecem nulas nos Parquet dos demais anos. O esquema de referência (`teses.schema.json`) reúne 86 colunas, gerado de uma conversão de amostras dos três layouts (1987, 2004, 2013, 2020 e 2024); a chave não é declarada: ver cuidados de uso.

## Cuidados de uso

- **Três layouts com nomes diferentes para o mesmo conceito.** Região é `regiao` (1987 a 2012) e `nm_regiao` (2013 em diante); UF é `uf` e `sg_uf_ies`; grande área é `grandeareadescricao` e `grande_area`; páginas são `numeropaginas` e `nr_paginas`. Para uma série longa, una as colunas com `coalesce`. Evidência: esquemas das amostras de 1987, 2013 e 2024 (conferido em 2026-11-09, versão 0.3.0).
- **`resumo` e `abstract`.** Nos layouts B e C (2013 em diante), `resumo` é o resumo em português (`DS_RESUMO`) e `abstract` o abstract em inglês (`DS_ABSTRACT`). No layout A (1987 a 2012) só existe `resumo` (de `ResumoTese`), sem `abstract`. A coluna `ds_resumo` não existe mais. Um lake convertido antes desta separação tem `resumo` com o abstract em inglês e `ds_resumo` com o português; apague `capes/teses` do lake e converta de novo.
- **Datas em três formatos de texto.** `dd/mm/aaaa`, `dd/mm/aaaa hh:mm:ss` e `27MAR2024:00:00:00` (mês abreviado em inglês). Converta por era antes de comparar.
- **Valores ausentes aparecem de formas diferentes.** Vazio (nulo no lake), `NÃO INFORMADO`, `NA` e `NÃO SE APLICA` convivem; `nr_paginas`/`numeropaginas` valem `0` em 534 de 2.162 linhas na amostra de 2024 e em 285 de 4.496 na de 1987, o que provavelmente significa páginas não informadas (hipótese, a fonte não define).
- **CPF e nomes.** `documento_discente` e `documentoorientador_*` são o CPF mascarado pela fonte, mas ainda são dados pessoais; em 1987, quase todas as linhas da amostra trazem o mesmo valor `999*****999`. `autor`, `orientador` e `coorientador` são nomes de pessoas; trate o dado conforme a legislação de proteção de dados.
- **Sem chave única entre eras.** O layout A não tem identificador de trabalho. Nos layouts B e C, `id_add_producao_intelectual` é único por linha nas amostras de 2013, 2020 e 2024, e o metadado oficial a lista como chave junto com o ano-base e o programa.
- **Anos faltantes no bruto.** O bruto conferido não tem 2017 nem 2021. Qualquer série anual por ano de defesa terá buracos nesses dois anos até que sejam coletados.
- **Reenvios.** Segundo a fonte, os programas podem retificar dados depois do envio, e o metadado de 2021 a 2024 afirma que os anos de 2021 e 2022 foram atualizados com a reabertura do calendário; a versão coletada de cada ano pode mudar.

## Exemplos

Como as colunas mudam entre os layouts, leia cada ano separadamente e una com `how="diagonal"`. Trabalhos por ano, grande área e grau acadêmico em 2018 a 2024 (layout C, que traz `grande_area`):

```python
from pathlib import Path

import polars as pl

raiz = Path("lake/capes/teses")
teses = pl.concat(
    [
        pl.scan_parquet(d / "*.parquet").with_columns(ano=pl.lit(int(d.name[4:])))
        for d in sorted(raiz.glob("ano=[0-9]*"))
    ],
    how="diagonal",
)
resumo = (
    teses.filter(pl.col("ano").is_between(2018, 2024))
    .group_by("ano", "grande_area", "grau_academico")
    .agg(pl.len().alias("trabalhos"))
    .sort("ano", "grande_area", "grau_academico")
    .collect()
)
```

Trabalhos por ano e região da instituição, unindo as duas grafias da região (`regiao` no layout A, `nm_regiao` nos layouts B e C):

```python
por_regiao = (
    teses.with_columns(pl.coalesce("regiao", "nm_regiao").alias("regiao_ies"))
    .group_by("ano", "regiao_ies")
    .agg(pl.len().alias("trabalhos"))
    .sort("ano", "regiao_ies")
    .collect()
)
```

Lembre que o bruto conferido não tem os anos 2017 e 2021.

## Referências

- Pacote 2021 a 2024: https://dadosabertos.capes.gov.br/dataset/2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil
- Pacote 2017 a 2020: https://dadosabertos.capes.gov.br/dataset/2017-2020-catalogo-de-teses-e-dissertacoes-da-capes
- Pacote 2013 a 2016: https://dadosabertos.capes.gov.br/dataset/catalogo-de-teses-e-dissertacoes-de-2013-a-2016
- Pacote 1987 a 2012: https://dadosabertos.capes.gov.br/dataset/1987-a-2012-catalogo-de-teses-e-dissertacoes-brasil
- Metadados (dicionário de variáveis): https://metadados.capes.gov.br/index.php/catalog/336 (2021 a 2024), https://metadados.capes.gov.br/index.php/catalog/288 (2017 a 2020), https://metadados.capes.gov.br/index.php/catalog/115 (2013 a 2016) e https://metadados.capes.gov.br/index.php/catalog/181 (1987 a 2012)
- Catálogo de Teses e Dissertações da CAPES: https://catalogodeteses.capes.gov.br
