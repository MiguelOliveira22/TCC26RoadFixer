# Dados contextuais externos

Coloque nesta pasta os arquivos abaixo e execute:

```powershell
python -m RoadFixerAPI.ModeloEstatistico.grid_search --external-dir RoadFixerAPI/ModeloEstatistico/data_tau/external
```

Os arquivos contextuais complementares são opcionais. A fonte de tráfego é obrigatória para calcular a taxa por veículos-km; sem exposição válida o treinamento é interrompido e a aplicação identifica o uso do fallback histórico.

O diretório `ProcessamentoParametros/weather-data` não é usado como clima mensal por padrão: os arquivos existentes em `data/weather-data` são cache de ocorrências e não seguem o formato do INMET. Para incluir clima, forneça `weather.csv` no formato descrito abaixo.

Os arquivos diários da ARTESP, por exemplo `raw/contagem_diaria_2025.csv`, também são lidos diretamente: não é necessário renomeá-los. Baixe `2020` a `2025` e coloque todos nesse diretório. O importador filtra `SP330`, soma `QTD_MOTO`, `QTD_PASSEIO` e `QTD_COMERCIAL` como fluxo, e usa `QTD_COMERCIAL` como veículos pesados.

Os cadastros da ARTESP exportados para `raw/cci_malha_rodoviaria_sp-MALHA_RODOVIARIA_SP.csv` e `raw/acessos_rodoviarios.csv` são carregados automaticamente. Eles acrescentam atributos de pista e contagens de acessos por km. Os demais CSVs `cci_malha_rodoviaria_sp-*.csv` representam outras abas e não entram nessa extração.

O fluxo da ARTESP é somado por mês e quilômetro. A exposição usada no alvo é aproximada como passagens mensais multiplicadas por uma célula de 1 km. Os dois sentidos são agregados para corresponder à chave `KM` disponível no painel; isso não substitui uma base de fluxo direcional. Linhas sem exposição válida não participam do treinamento da taxa.

| Arquivo | Campos obrigatórios | Fonte e uso |
| --- | --- | --- |
| `traffic.csv` | `data,km,volume_total` | Dados de SAT ou praças da ARTESP. Aceita `veiculos_pesados` opcional. Para cada km, o sistema usa o contador mais próximo do mês anterior como preditor; o fluxo observado do mês forma o denominador histórico de veículos-km. |
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

O modelo prevê severidade ponderada por milhão de veículos-km. O índice de 0 a 10 publicado pela API é uma ordenação relativa entre os quilômetros do mês previsto, não uma probabilidade. A faixa de previsão usa o erro absoluto observado no ano de teste como referência e pode não cobrir mudanças futuras nos dados.
