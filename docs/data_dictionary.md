# Dicionário de dados

A camada `data/curated/` contém produtos agregados a partir dos arquivos anuais do MDIC/SECEX. A primeira versão cobre 2023 e 2024, nos fluxos de exportação (`EXP`) e importação (`IMP`).

## `comercio_anual_pais`

Uma linha representa um ano, fluxo e país. O produto serve para ranking, participação, séries históricas curtas e visualizações de parceiros.

| Campo | Descrição |
|---|---|
| `ano` | Ano de referência. |
| `fluxo` | `EXP` para exportação ou `IMP` para importação. |
| `codigo_pais` | Código de país do MDIC. Deve ser tratado como texto. |
| `nome_pais` | Nome do país na tabela auxiliar oficial. |
| `pais_iso3` | Código ISO de três letras, quando disponível. |
| `valor_fob_usd` | Soma do valor FOB em dólares. |
| `kg_liquido` | Soma do peso líquido em quilogramas. |
| `linhas_origem` | Quantidade de linhas do arquivo bruto agregadas. |
| `participacao` | Participação do país no valor FOB do fluxo e ano. Varia de 0 a 1. |

## `comercio_mensal_pais`

Uma linha representa um ano, mês, fluxo e país. Possui as mesmas métricas principais de `comercio_anual_pais` e permite análises de sazonalidade.

## `ranking_parceiros`

O produto acrescenta `ranking_anual`, que ordena os países dentro de cada ano e fluxo, e `valor_fob_acumulado_usd`, que soma o valor corrente do país ao longo dos anos disponíveis. O acumulado não deve ser interpretado como valor anual.

## `saldo_comercial_pais`

Uma linha representa um ano e país. As colunas `exportacoes_usd` e `importacoes_usd` usam valor FOB. `saldo_usd` é calculado como exportações menos importações.

## Fonte e atualização

Os produtos foram gerados diretamente dos CSVs anuais abertos do [MDIC](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta), usando a tabela auxiliar oficial de países. O arquivo `catalog.json` registra URLs, arquivos de origem, tamanhos e hashes SHA-256.

O ano mais recente pode sofrer revisões. Uma nova versão deve ser publicada com novo catálogo e novo checksum, sem sobrescrever silenciosamente a versão anterior.
