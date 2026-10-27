# Brasil Comércio Exterior Dados

Pipeline reprodutível para transformar os dados públicos oficiais do MDIC/SECEX (Comex Stat) em datasets analíticos prontos para uso: Parquet, DuckDB e tabelas agregadas por país/ano para análises, dashboards e bar chart race.

> Projeto de portfólio: o código é executável localmente, mas os CSVs oficiais não são versionados no Git por causa do tamanho. Cada carga registra URL, período, fluxo, hash SHA-256, tamanho e data de captura.

## **O que este MVP entrega**

- Download configurável dos CSVs anuais oficiais de exportação/importação.

- Preservação da origem em `data/raw/` e manifesto de ingestão.

- Normalização tipada para Parquet, mantendo códigos como texto.

- Banco DuckDB local para consultas analíticas.

- `mart_comercio_anual_pais`: valor FOB e kg líquido por ano, fluxo e país.

- `mart_ranking_parceiros`: ranking anual e valor acumulado, separados para não confundir os conceitos.

- Testes unitários e de qualidade com fixture pequena.

- CI no GitHub Actions.

## Fonte e escopo metodológico

A fonte canônica é o [Comex Stat/MDIC](https://comexstat.mdic.gov.br/pt/home). Para grandes volumes, este projeto usa os arquivos abertos anuais; a [API oficial](https://api-comexstat.mdic.gov.br/docs/) fica reservada para consultas pequenas e validações. O MVP começa em 1997, quando a série passa a usar NCM/SISCOMEX. O período histórico 1989–1996 usa NBM e metodologia distinta, portanto fica fora do primeiro produto comparável.

O fato detalhado mantém o grão oficial: ano, mês, NCM, unidade, país, UF, via e URF. Os marts de parceiros agregam por ano, fluxo e país. `VL_FOB` é valor em dólares no local de embarque; `KG_LIQUIDO` é peso líquido. O ano corrente pode ser parcial/preliminar e revisões do MDIC podem alterar períodos recentes.

## Início rápido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Baixa e processa um ano (arquivos podem ser grandes)
python -m brasil_comex ingest --year 2023 --flows EXP IMP
python -m brasil_comex transform --year 2023
python -m brasil_comex validate --year 2023
```

Para testar sem baixar dados oficiais:

```bash
pytest -q
python -m brasil_comex transform --input tests/fixtures --output-dir /tmp/comex-demo
```

## Estrutura

```
config/                  parâmetros e URLs da fonte
data/raw/                snapshots originais + manifestos (não versionar no Git)
data/reference/          tabelas auxiliares e totais oficiais do MDIC
data/staged/             Parquet normalizado
data/mart/               DuckDB/Parquet agregados para consumo
src/brasil_comex/        ingestão, transformação e validação
tests/                   testes e fixtures pequenas
docs/                    arquitetura, pesquisa e decisões metodológicas
.github/workflows/       CI
```

## Atualização recomendada

Faça a carga histórica uma vez. Depois, reprocessar o último ano disponível mensalmente; após a revisão anual, reprocessar o ano anterior. Nunca sobrescreva um snapshot sem registrar nova versão: a fonte pode ser revisada.

## Publicação

- **GitHub:** código, schemas, documentação, manifestos, testes e releases tagueadas.

- **GitHub Releases ou armazenamento de objetos:** Parquet/DuckDB derivados grandes, com checksum e contagem de linhas.

- **Kaggle:** cópia secundária para notebooks e exploração, sempre apontando de volta para este repositório e para o MDIC.

- **Catálogo DCAT/CKAN:** metadados, cobertura, periodicidade, licença, `accessURL` e `downloadURL`.

Não coloque CSVs brutos grandes no histórico Git. Verifique a licença do arquivo exato antes de redistribuir dados; a licença do código deste projeto não licencia automaticamente os dados do MDIC.

## Limitações importantes

- Os dados são estatísticas agregadas de bens, não microdados de empresas.

- Município no módulo municipal representa o domicílio fiscal do declarante, não necessariamente origem física ou local de produção.

- FOB, CIF, frete e seguro são medidas diferentes; não misture sem nota metodológica.

- NCM e descrições têm vigência. Mantenha códigos e tabelas de correlação oficiais.

- Uma corrida de barras é narrativa exploratória. Publique também tabela, série estática, participação e variação.

## Referências

- [Base de dados bruta do MDIC](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)

- [Perguntas frequentes do Comex Stat](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/perguntas-frequentes-faq)

- [DuckDB e Parquet](https://duckdb.org/docs/2.0/data/parquet/overview.html)

- [Princípios FAIR](https://doi.org/10.1038/sdata.2016.18)

- [Reprodutibilidade computacional](https://doi.org/10.1371/journal.pcbi.1003285)