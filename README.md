# capes-fetcher

[![CI](https://github.com/Quantilica/capes-fetcher/actions/workflows/test.yml/badge.svg)](https://github.com/Quantilica/capes-fetcher/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Coletor e conversor Lake Hive para dados abertos de **Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES)** (`capes`), parte do ecossistema [Quantilica](https://quantilica.com).

## Instalação

### Via CLI Quantilica (recomendado)

```bash
quantilica install capes
```

Para instalar com suporte à conversão Parquet Lake:

```bash
quantilica install capes --extra analysis
```

### Como biblioteca Python

```bash
uv add capes-fetcher --index https://index.quantilica.com/simple/
```

Com o extra de análise analítica:

```bash
uv add 'capes-fetcher[analysis]' --index https://index.quantilica.com/simple/
```

## Uso via CLI

```bash
# Listar conjuntos disponíveis
quantilica capes list

# Catálogo completo (R1 + listados) e descoberta de novidades na fonte
quantilica capes catalogo bolsas
quantilica capes discover

# Verificar novos arquivos e frescor
quantilica capes check

# Sincronizar arquivos para o diretório local bruto
quantilica capes sync -o /data/capes

# Converter acervo bruto para o Universal Hive Parquet Lake
quantilica capes convert /data/capes /data/lake
```

## Cobertura do catálogo

O CKAN da CAPES publica 89 pacotes (2026-11-03), fatias por era de 26 temas.
O catálogo cobre os 89, em 11 grupos.

| Grupo | Temas | Pacotes | R1 (baixa) | Listado |
|---|---:|---:|---:|---:|
| teses | 1 | 4 | 4 | 0 |
| programas | 1 | 3 | 3 | 0 |
| cursos | 1 | 3 | 3 | 0 |
| pessoas | 2 | 8 | 0 | 8 |
| producao | 3 | 16 | 0 | 16 |
| projetos | 3 | 11 | 0 | 11 |
| bolsas | 5 | 17 | 0 | 17 |
| formacao-professores | 4 | 8 | 0 | 8 |
| fomento | 3 | 9 | 0 | 9 |
| periodicos | 1 | 5 | 0 | 5 |
| gestao | 2 | 5 | 0 | 5 |

`list` e `sync` operam só no tier R1 (10 pacotes). O servidor da CAPES é lento
(`package_list` em ~130 s); os comandos que consultam o CKAN podem demorar.

## Documentação dos dados

O que cada dataset contém, de onde vem, como chega ao lake e os cuidados de uso: [docs/README.md](docs/README.md).

## Licença

Distribuído sob licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.
