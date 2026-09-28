# Grid Search para trechos emergenciais

Execute, a partir da raiz do projeto, depois de instalar as dependências:

```powershell
python -m pip install -r requirements.txt
python -m RoadFixerAPI.ModeloEstatistico.grid_search
```

O processo usa os CSVs processados em `RoadFixerAPI/data/accidents/processed`. Para cada km e mês, ele prevê a severidade no mês seguinte com o histórico de 30, 90 e 365 dias. A busca escolhe os parâmetros pela **média da captura mensal** de severidade no topo de 10% dos km. O último ano completo fica separado como teste final; um ano corrente parcial é usado apenas no refit final para prever o próximo mês.

A grade foi mantida compacta para poder rodar no fluxo do projeto. Para uma pesquisa offline, amplie `param_grid` em `grid_search.py`; não misture esse teste com o conjunto do último ano.

## Integração dos fatores de risco

O diretório [`data_tau/external`](data_tau/external/README.md) contém o contrato dos CSVs que o modelo recebe. Por padrão ele é carregado automaticamente. O GridSearch adiciona fluxo, percentual de pesados, atributos de infraestrutura e calendário. Medições de tráfego, clima e velocidade são deslocadas para o mês seguinte, para que a previsão não veja dados que ainda não existiriam na data de emissão.

Os arquivos gerados são:

- `RoadFixerAPI/ModeloEstatistico/data_tau/grid_search_report.json`: parâmetros escolhidos, métricas e importância das variáveis.
- `RoadFixerAPI/ModeloEstatistico/data_tau/ranking_km_previsto.csv`: resultado do teste histórico.
- `RoadFixerAPI/ModeloEstatistico/data_tau/ranking_km_proximo_mes.csv`: ranking operacional do próximo mês.
- `RoadFixerAPI/API/content/accident-history/risk/savedData.json`: índice de priorização consumido por `/riskData`.

## Dados que fazem diferença

Os dados existentes permitem começar com data, km, vítimas e tipo de acidente. Para um ranking que represente risco, e não apenas volume de registros, inclua também:

- exposição: fluxo por faixa/hora, percentual de pesados e velocidade média; sem ela, um km movimentado tende a parecer perigoso mesmo se sua taxa de acidente for normal;
- via: número e largura de faixas, curvas, aclives, acostamento, iluminação, limite de velocidade, interseções e obras;
- condições: chuva, visibilidade, vento, temperatura, dia da semana, feriados e horário;
- ocorrências operacionais: congestionamento, panes, animais na pista e intervenções anteriores;
- denominador e qualidade: extensão do segmento, período de cobertura, coordenadas e campos ausentes.

Não use como variável de entrada para prever o próximo mês a gravidade, vítimas ou causa do próprio acidente futuro: eles só podem ser usados como alvo histórico. O índice publicado é uma ferramenta de triagem humana, não uma probabilidade de acidente. Calibre os pesos de severidade com a equipe de segurança viária e acompanhe diferenças por município e tipo de usuário da via.
