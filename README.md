# Brasil Comércio Exterior Dados

Dados tratados e pipeline reprodutível para estatísticas oficiais de comércio exterior do Brasil.

O projeto transforma os arquivos do [Comex Stat/MDIC](https://comexstat.mdic.gov.br/pt/home) em produtos prontos para visualizações, dashboards, análises e jornalismo de dados. A ideia é que outros projetos consultem os dados já organizados, sem repetir download, limpeza e tratamento.

## Como usar em outro projeto

A camada de consumo é a `data/curated/`. Ela reúne tabelas pequenas e estáveis, pensadas para serem lidas diretamente por Python, R, DuckDB, Power BI, Tableau, Flourish ou Datawrapper.

Os principais produtos são:

```text
data/curated/
├── comercio_anual_pais.csv
├── comercio_anual_pais.parquet
├── comercio_mensal_pais.parquet
├── ranking_parceiros.csv
├── saldo_comercial_pais.csv
└── catalog.json
```

### Python

```python
import pandas as pd

url = (
    "https://raw.githubusercontent.com/letstahl/brasil-comex-data/"
    "main/data/curated/comercio_anual_pais.csv"
)

dados = pd.read_csv(url)
exportacoes = dados[dados["fluxo"] == "EXP"]
```

### DuckDB

```sql
SELECT ano, nome_pais, valor_fob_usd
FROM read_parquet(
  'https://raw.githubusercontent.com/letstahl/brasil-comex-data/main/data/curated/comercio_anual_pais.parquet'
)
WHERE fluxo = 'EXP'
ORDER BY ano, valor_fob_usd DESC;
```

### R

```r
library(readr)

url <- paste0(
  "https://raw.githubusercontent.com/letstahl/brasil-comex-data/",
  "main/data/curated/comercio_anual_pais.csv"
)

dados <- read_csv(url)
```

O `catalog.json` informa a versão, o período coberto, a fonte, a data de atualização, as métricas e o checksum de cada produto.

## O que cada produto representa

`comercio_anual_pais` agrega exportações e importações por ano e país. `comercio_mensal_pais` mantém a dimensão mensal para análises de sazonalidade. `ranking_parceiros` separa o ranking de cada ano do valor acumulado. `saldo_comercial_pais` combina exportações e importações para calcular o saldo por parceiro.

O ranking anual e o valor acumulado não respondem à mesma pergunta. O primeiro mostra quem liderou em determinado ano; o segundo mostra a soma dos valores até aquele ano.

## Reproduzir o pipeline

### Instalação

```bash
git clone https://github.com/letstahl/brasil-comex-data.git
cd brasil-comex-data

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Teste rápido sem baixar a base oficial

A fixture incluída permite testar o fluxo completo em poucos segundos:

```bash
pytest -q
ruff check src tests

python -m brasil_comex transform \
  --input tests/fixtures \
  --output-dir /tmp/comex-demo

python -m brasil_comex validate \
  --database /tmp/comex-demo/comex.duckdb
```

### Processar dados oficiais

A ingestão pode ser executada por ano e por fluxo:

```bash
python -m brasil_comex ingest --year 2023 --flows EXP IMP
python -m brasil_comex transform --input data/raw/year=2023 --output-dir data/mart
python -m brasil_comex validate --database data/mart/comex.duckdb
```

Os CSVs oficiais são grandes. Para cargas completas, o uso de DuckDB ou de um ambiente com espaço suficiente é recomendado; planilhas não são adequadas para essa etapa.

### Gerar a camada curada

O gerador reproduz a primeira publicação da camada de consumo. Por padrão, processa os anos de 2023 e 2024:

```bash
python -m brasil_comex.build_curated \
  --years 2023 2024 \
  --output-dir data/curated
```

O [dicionário de dados](docs/data_dictionary.md) descreve as colunas, o grão e as métricas de cada produto. O `catalog.json` registra as fontes e os hashes dos arquivos usados na geração.

## Fonte e metodologia

A série principal começa em 1997, quando a base passa a utilizar NCM/SISCOMEX. O período de 1989 a 1996 utiliza NBM e metodologia diferente, permanecendo separado.

A base detalhada mantém o grão publicado pelo MDIC: ano, mês, NCM, unidade estatística, país, UF, via e URF. As métricas principais são `VL_FOB`, valor FOB em dólares, e `KG_LIQUIDO`, peso líquido em quilogramas. `QT_ESTAT` deve ser interpretada junto com a unidade estatística da NCM.

FOB, CIF, frete e seguro possuem significados diferentes. O ano mais recente pode estar parcial ou sujeito a revisões da fonte.

## Estrutura

```text
config/                  URLs e parâmetros da fonte
data/curated/            produtos prontos para consumo
data/raw/                snapshots oficiais e manifestos
data/reference/          tabelas auxiliares e arquivos de validação
data/staged/             dados normalizados em Parquet
data/mart/               DuckDB e produtos analíticos
src/brasil_comex/        ingestão, transformação e validação
tests/                   testes e fixtures pequenas
docs/                    arquitetura, metodologia e pesquisa
.github/workflows/       CI do projeto
```

Os arquivos brutos e os artefatos detalhados não entram no histórico normal do Git. Produtos curados pequenos podem ser publicados no repositório; arquivos maiores devem ser distribuídos por releases anuais, com manifesto, checksum e versão da fonte.

## Atualização anual

A atualização ocorre quando uma nova versão anual da fonte é publicada:

```text
arquivo anual do MDIC
        ↓
ingestão e manifesto
        ↓
tratamento e validações
        ↓
produtos em data/curated/
        ↓
release anual no GitHub
```

Cada versão registra URL, período, fluxo, data de captura, tamanho, hash SHA-256 e status da fonte. Snapshots antigos não devem ser sobrescritos.

## Limitações

Os dados são estatísticas agregadas de comércio exterior de bens. Não são microdados de empresas e não permitem identificar empresas, CNPJ ou transações individuais.

No módulo municipal, o município representa o domicílio fiscal do declarante. Isso não significa necessariamente local de produção, origem física ou desembarque da mercadoria.

Mudanças de classificação, descrições, unidades e revisões podem afetar comparações históricas. Códigos e tabelas auxiliares oficiais devem ser preservados junto com cada versão.

## Fontes

- [Base de dados bruta do MDIC](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)
- [Documentação da API Comex Stat](https://api-comexstat.mdic.gov.br/docs/)
- [Perguntas frequentes do Comex Stat](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/perguntas-frequentes-faq)
- [DuckDB e Parquet](https://duckdb.org/docs/2.0/data/parquet/overview.html)
- [Princípios FAIR](https://doi.org/10.1038/sdata.2016.18)
- [Reprodutibilidade computacional](https://doi.org/10.1371/journal.pcbi.1003285)

## Licença

O código está disponível sob a licença MIT. Os dados do MDIC possuem fonte e regras próprias de uso; a licença do código não substitui a verificação dos direitos aplicáveis a cada arquivo distribuído.
