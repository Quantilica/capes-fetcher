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

# Verificar novos arquivos e frescor
quantilica capes check

# Sincronizar arquivos para o diretório local bruto
quantilica capes sync -o /data/capes

# Converter acervo bruto para o Universal Hive Parquet Lake
quantilica capes convert /data/capes /data/lake
```

## Licença

Distribuído sob licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.
