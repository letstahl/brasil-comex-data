# Brasil Comércio Exterior Dados

Pipeline e base analítica reutilizável para dados oficiais de comércio exterior do Brasil.

O projeto transforma os arquivos públicos do [Comex Stat/MDIC](https://comexstat.mdic.gov.br/pt/home) em dados estruturados para visualizações, dashboards, análises e jornalismo de dados. A proposta é evitar que cada projeto precise baixar os mesmos arquivos, consultar a API e repetir a limpeza.

> Status: MVP funcional. O repositório já contém o pipeline, os testes e uma fixture pequena para reprodução. A publicação da série histórica tratada será adicionada em releases anuais.

## Uso rápido

### 1. Instalação

```bash
git clone https://github.com/letstahl/brasil-comex-data.git
cd brasil-comex-data

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### 2. Reproduzir o exemplo local

A fixture incluída permite executar o pipeline sem baixar a base oficial:

```bash
pytest -q
ruff check src tests

python -m brasil_comex transform \
  --input tests/fixtures \
  --output-dir /tmp/comex-demo

python -m brasil_comex validate \
  --database /tmp/comex-demo/comex.duckdb
```

A execução gera Parquet, DuckDB e os seguintes produtos analíticos:

- `mart_comercio_anual_pais`: valor FOB e quilograma líquido por ano, fluxo e país;
- `mart_ranking_parceiros`: ranking anual e valor acumulado, mantidos separados;
- `fato_comex_ncm`: dados normalizados no grão original.

### 3. Processar um ano oficial

Os arquivos oficiais podem ser baixados e processados por ano:

```bash
python -m brasil_comex ingest --year 2023 --flows EXP IMP
python -m brasil_comex transform --input data/raw/year=2023 --output-dir data/mart
python -m brasil_comex validate --database data/mart/comex.duckdb
```

Os arquivos oficiais são grandes. O processamento completo deve ser feito com DuckDB ou em uma máquina com espaço suficiente; planilhas não são recomendadas.

## Dados e metodologia

O MVP trabalha com a série a partir de 1997, quando a base passa a utilizar NCM/SISCOMEX. O período de 1989 a 1996 utiliza NBM e metodologia diferente, por isso permanece separado.

A base detalhada mantém o grão publicado pelo MDIC: ano, mês, NCM, unidade estatística, país, UF, via e URF. A camada analítica agrega os registros por ano, fluxo e país.

As principais métricas são:

- `VL_FOB`: valor FOB em dólares;
- `KG_LIQUIDO`: peso líquido em quilogramas;
- `QT_ESTAT`: quantidade estatística, sempre interpretada com a unidade da NCM.

Exportações e importações não devem ser comparadas sem considerar a métrica usada. FOB, CIF, frete e seguro possuem significados diferentes. O ano mais recente pode estar parcial ou sujeito a revisões do MDIC.

## Estrutura do repositório

```text
config/                  URLs e parâmetros da fonte
data/raw/                snapshots oficiais e manifestos
data/reference/          tabelas auxiliares e arquivos de validação
data/staged/             dados normalizados em Parquet
data/mart/               DuckDB e produtos analíticos
src/brasil_comex/        ingestão, transformação e validação
tests/                   testes e fixtures pequenas
docs/                    arquitetura, metodologia e pesquisa
.github/workflows/       CI do projeto
```

Os arquivos brutos e os artefatos grandes não entram no histórico normal do Git. A ideia é publicar os produtos curados em releases anuais, com manifesto, checksum, período coberto e versão da fonte.

## Atualização

A atualização prevista é anual. O fluxo recomendado é:

```text
novo arquivo do MDIC
        ↓
ingestão e manifesto
        ↓
tratamento e validações
        ↓
produtos curados
        ↓
release anual no GitHub
```

Cada carga deve registrar a URL, o período, o fluxo, a data de captura, o tamanho e o hash SHA-256. Snapshots antigos não devem ser sobrescritos sem uma nova versão.

## Limitações

Os dados são estatísticas agregadas de comércio exterior de bens. Não são microdados de empresas e não permitem identificar empresas, CNPJ ou transações individuais.

No módulo municipal, o município representa o domicílio fiscal do declarante. Isso não significa necessariamente local de produção, origem física ou desembarque da mercadoria.

Mudanças de classificação, descrições, unidades e revisões da fonte podem afetar comparações históricas. Códigos e tabelas auxiliares oficiais devem ser preservados junto com cada versão do dataset.

## Fontes e referências

- [Base de dados bruta do MDIC](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)
- [Documentação da API Comex Stat](https://api-comexstat.mdic.gov.br/docs/)
- [Perguntas frequentes do Comex Stat](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/perguntas-frequentes-faq)
- [DuckDB e Parquet](https://duckdb.org/docs/2.0/data/parquet/overview.html)
- [Princípios FAIR](https://doi.org/10.1038/sdata.2016.18)
- [Reprodutibilidade computacional](https://doi.org/10.1371/journal.pcbi.1003285)

## Licença

O código está disponível sob a licença MIT. Os dados do MDIC possuem fonte e regras próprias de uso; a licença do código não substitui a verificação dos direitos aplicáveis a cada arquivo distribuído.
