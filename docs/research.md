# Pesquisa e decisões técnicas

A arquitetura foi definida a partir da documentação oficial do MDIC/SECEX e de referências sobre dados abertos, reprodutibilidade e ferramentas analíticas.

## Decisões principais

**Fonte.** Os arquivos abertos do MDIC são a fonte principal para cargas grandes. A API do Comex Stat fica indicada para consultas menores e validações, pois possui limites de tempo e quantidade de linhas.

**Reprodutibilidade.** Cada carga deve registrar fonte, URL, período, data de captura, versão do layout, classificações utilizadas, hash e parâmetros de transformação. O objetivo é permitir que outra pessoa refaça a mesma versão do dataset.

**Arquitetura.** O fluxo usa três camadas: `raw`, para preservar a origem; `staged`, para padronizar os dados; e `mart`, para publicar tabelas prontas para análise. Parquet funciona como formato analítico e DuckDB como ferramenta local de transformação e consulta.

**Publicação.** O GitHub concentra código, documentação, testes, manifestos e versões. Os datasets curados pequenos podem ficar disponíveis diretamente no repositório. Arquivos detalhados maiores devem ser publicados em releases anuais ou em armazenamento apropriado, sempre com checksum e link para a fonte oficial.

**Visualização.** A análise de parceiros deve agregar os registros por ano, fluxo e país. Um ranking anual mostra o valor daquele ano; um ranking acumulado mostra a soma corrente. Os dois indicadores não devem ser tratados como equivalentes. A animação deve vir acompanhada de tabela ou série estática.

## Fontes consultadas

- [MDIC — base de dados bruta](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)
- [Comex Stat — portal oficial](https://comexstat.mdic.gov.br/pt/home)
- [API Comex Stat](https://api-comexstat.mdic.gov.br/docs/)
- [Manual do Comex Stat](https://balanca.mdic.gov.br/balanca/manual/Manual.pdf)
- [Apache Parquet](https://parquet.apache.org/docs/overview/)
- [DuckDB — Parquet](https://duckdb.org/docs/2.0/data/parquet/overview.html)
- [dbt — sources](https://docs.getdbt.com/docs/build/sources)
- [Open Definition 2.1](https://opendefinition.org/od/2.1/en/)
- [FAIR principles](https://doi.org/10.1038/sdata.2016.18)
- [Reproducible computational research](https://doi.org/10.1371/journal.pcbi.1003285)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/)
