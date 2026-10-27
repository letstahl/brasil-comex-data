# Pesquisa e decisões

A pesquisa consultou documentação oficial do MDIC/SECEX, API do Comex Stat, manuais metodológicos, literatura de dados abertos e reprodutibilidade, além de documentação de Parquet, DuckDB, dbt, GitHub, Kaggle e DCAT/CKAN.

## Conclusões aplicadas

1. **Fonte canônica:** usar CSVs da base aberta do MDIC para cargas grandes e a API do Comex Stat para consultas pequenas e validações. A própria API informa limites de tempo e quantidade de linhas.
2. **Reprodutibilidade:** guardar código, parâmetros, data de captura, URL, hash, versão do esquema, classificações e notas metodológicas. Isso segue os princípios FAIR e recomendações de workflows computacionais reproduzíveis.
3. **Tecnologia:** CSV original em `raw`, Parquet em `staged/mart` e DuckDB para ELT local. O desenho mantém interoperabilidade e permite filtros eficientes.
4. **Publicação:** GitHub como fonte canônica de código/documentação; releases ou object storage para artefatos grandes; Kaggle como distribuição secundária; catálogo DCAT/CKAN para descoberta.
5. **Visualização:** agregação anual por país com `VL_FOB` e `KG_LIQUIDO`; ranking anual e acumulado devem ser separados. A animação precisa vir acompanhada por tabela e série estática.

## Fontes

- [MDIC — base de dados bruta](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)
- [Comex Stat — portal oficial](https://comexstat.mdic.gov.br/pt/home)
- [API Comex Stat — documentação](https://api-comexstat.mdic.gov.br/docs/)
- [MDIC — perguntas frequentes](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/perguntas-frequentes-faq)
- [Manual do Comex Stat](https://balanca.mdic.gov.br/balanca/manual/Manual.pdf)
- [Apache Parquet](https://parquet.apache.org/docs/overview/)
- [DuckDB — Parquet](https://duckdb.org/docs/2.0/data/parquet/overview.html)
- [dbt — sources](https://docs.getdbt.com/docs/build/sources)
- [Open Definition 2.1](https://opendefinition.org/od/2.1/en/)
- [FAIR principles](https://doi.org/10.1038/sdata.2016.18)
- [Ten simple rules for reproducible computational research](https://doi.org/10.1371/journal.pcbi.1003285)
- [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/)
- [Flourish — bar chart race](https://helpcenter.flourish.studio/hc/en-us/articles/8761566757647-Bar-chart-race-an-overview)
