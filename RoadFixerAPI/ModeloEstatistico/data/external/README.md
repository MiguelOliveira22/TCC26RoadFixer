# Dados contextuais externos

Coloque nesta pasta os arquivos abaixo e execute:

```powershell
python RoadFixerAPI/ModeloEstatistico/grid_search.py --external-dir RoadFixerAPI/ModeloEstatistico/data/external
```

Todos os arquivos são opcionais. A ausência de uma fonte não interrompe a execução.

O histórico do INMET que já existe em `ProcessamentoParametros/weather-data` é carregado automaticamente como chuva e vento. Ele corresponde à estação São Paulo–Mirante, portanto é uma referência regional; para maior precisão nos trechos mais distantes, forneça um `weather.csv` com estações ou grade meteorológica próximas àquele km.

Os arquivos diários da ARTESP, por exemplo `raw/contagem_diaria_2025.csv`, também são lidos diretamente: não é necessário renomeá-los. Baixe `2020` a `2025` e coloque todos nesse diretório. O importador filtra `SP330`, soma `QTD_MOTO`, `QTD_PASSEIO` e `QTD_COMERCIAL` como fluxo, e usa `QTD_COMERCIAL` como veículos pesados.

Os arquivos oficiais `raw/cci_malha_rodoviaria_sp.xlsx` e `raw/acessos_rodoviarios.xlsx` também são carregados automaticamente. Eles acrescentam `pista_dupla`, `trecho_planejado`, quantidade de acessos, acessos comerciais, não autorizados, não conformes e em condição ruim por km.

| Arquivo | Campos obrigatórios | Fonte e uso |
| --- | --- | --- |
| `traffic.csv` | `data,km,volume_total` | Dados de SAT ou praças da ARTESP. Aceita `veiculos_pesados` opcional. Para cada km, o sistema usa o contador mais próximo no mesmo mês. |
| `weather.csv` | `data,precipitacao_mm` | INMET ou Open-Meteo; `vento_kmh` e `visibilidade_km` são opcionais. Use estações/grades próximas à rodovia. |
| `speed.csv` | `data,km,velocidade_media_kmh` | Concessionária ou fornecedor de mobilidade autorizado. `velocidade_livre_kmh` é opcional; com ela é calculado o índice de congestionamento. |
| `works.csv` | `inicio,fim,km_inicial,km_final` | Programação de obras da ARTESP ou informação da concessionária. `intensidade` é opcional, de 0 a 1. |
| `infrastructure.csv` | `km_inicial,km_final` | Cadastro técnico/geometria do DER, ARTESP ou concessionária. Campos opcionais: `n_faixas`, `limite_velocidade_kmh`, `declive_percent`, `raio_curva_m`, `iluminacao`, `acostamento_m`, `acessos_por_km`. |

Exemplo mínimo de `traffic.csv`:

```csv
data,km,volume_total,veiculos_pesados
2025-01-01,98,18340,4912
2025-01-01,107,21100,5390
```

Não inclua vítimas, gravidade ou causa do acidente em arquivos de contexto: essas variáveis formam o resultado que se pretende prever, e incluí-las produziria vazamento de informação.
