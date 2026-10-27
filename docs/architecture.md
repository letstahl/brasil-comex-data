# Arquitetura

## Decisão

O projeto adota uma arquitetura local-first em três camadas. `raw` preserva o arquivo oficial sem edição; `staged` normaliza tipos e mantém o grão original; `mart` publica produtos analíticos para consumo. A escolha reduz dependência de ferramentas pagas e permite executar o mesmo pipeline em laptop, CI ou depois em armazenamento de objetos.

## Grão e modelos

A fonte detalhada do MDIC é uma linha por ano, mês, NCM, unidade estatística, país, UF do produto, via e URF. Exportação possui `VL_FOB`, `KG_LIQUIDO` e `QT_ESTAT`; importação acrescenta frete e seguro. O MVP mantém essas colunas e adiciona `fluxo`.

O primeiro mart agrega por `ano`, `fluxo` e `codigo_pais`, calculando valor FOB, quilograma líquido e quantidade de linhas. O ranking anual e o valor acumulado são colunas distintas: o primeiro responde “quem liderou naquele ano?”; o segundo responde “qual foi o total corrente até aquele ano?”.

## Atualização

A carga histórica deve ser feita uma vez. Em seguida, reprocessa-se o último ano disponível conforme a divulgação mensal e o ano anterior após a revisão anual. Cada download gera manifesto com URL, timestamp, tamanho e SHA-256. Snapshots não devem ser sobrescritos sem nova versão.

## Validações

A qualidade mínima inclui contrato de colunas, códigos como texto, meses entre 1 e 12, chaves não nulas, medidas não negativas e reconciliação com os arquivos de totais de conferência do MDIC. Na evolução do projeto, adicionar tabelas auxiliares de país/NCM/unidades, freshness e testes de distribuição.

## Extensões

A segunda etapa pode adicionar dbt para lineage e documentação, domínio municipal separado e um notebook que exporte o formato largo necessário para Flourish ou outra ferramenta de bar chart race. A série 1989–1996 deve continuar isolada, pois usa NBM e metodologia distinta.
