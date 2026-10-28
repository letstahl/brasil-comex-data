# Arquitetura do projeto

## Objetivo

O projeto separa a obtenção dos dados, o tratamento e o consumo analítico. Essa separação permite atualizar a fonte sem refazer manualmente as análises e facilita o uso dos produtos em notebooks, dashboards e reportagens.

## Camadas

### Raw

A camada `raw` guarda os arquivos oficiais sem edição. Cada carga recebe um manifesto com URL, ano, fluxo, data de captura, tamanho e hash SHA-256.

### Staged

A camada `staged` padroniza os tipos, preserva os códigos como texto e mantém o grão original do Comex Stat. Essa etapa não deve substituir códigos nem descrições históricas por valores digitados manualmente.

### Mart

A camada `mart` reúne as tabelas destinadas ao consumo. O primeiro produto agrega os dados por ano, fluxo e país, calculando valor FOB, quilograma líquido e número de linhas de origem. O ranking anual e o valor acumulado aparecem em campos diferentes para evitar interpretações equivocadas.

## Grão dos dados

A base detalhada do MDIC contém ano, mês, NCM, unidade estatística, país, UF, via e URF. A exportação possui valor FOB, quilograma líquido e quantidade estatística; a importação também pode conter frete e seguro.

A base municipal deve ser tratada como um domínio separado. O município representa o domicílio fiscal do declarante e não necessariamente o local de produção ou de embarque.

## Reprodução

A reprodução local pode ser feita com a fixture incluída:

```bash
pytest -q
python -m brasil_comex transform --input tests/fixtures --output-dir /tmp/comex-demo
python -m brasil_comex validate --database /tmp/comex-demo/comex.duckdb
```

Para uma carga oficial, o pipeline baixa um ano específico:

```bash
python -m brasil_comex ingest --year 2023 --flows EXP IMP
python -m brasil_comex transform --input data/raw/year=2023 --output-dir data/mart
```

## Atualização

A atualização prevista é anual. Uma nova versão deve baixar o arquivo do ano, preservar o snapshot, executar as validações, gerar os produtos curados e publicar uma release com manifesto e checksum.

A série de 1989 a 1996 permanece fora do primeiro produto comparável porque usa NBM e metodologia diferente da série iniciada em 1997.
