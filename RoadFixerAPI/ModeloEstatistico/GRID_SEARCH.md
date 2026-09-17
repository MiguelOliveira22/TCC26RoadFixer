# Grid Search para trechos emergenciais

Execute, a partir da raiz do projeto, depois de instalar as dependências:

```powershell
python -m pip install -r requirements.txt
python RoadFixerAPI/ModeloEstatistico/grid_search.py
```

O processo usa os CSVs `p*.csv` de acidentes da Anhanguera. Para cada km e mês, ele prevê a severidade no mês seguinte com o histórico de 30, 90 e 365 dias. A busca escolhe os parâmetros que capturam a maior parcela da severidade real ao priorizar o topo de 10% dos km. O último ano fica separado como teste final; portanto, ele não é usado para escolher os parâmetros.

A grade foi mantida compacta para poder rodar no fluxo do projeto. Para uma pesquisa offline, amplie `param_grid` em `grid_search.py`; não misture esse teste com o conjunto do último ano.

## Integração dos fatores de risco

O diretório [`data/external`](data/external/README.md) contém o contrato dos CSVs que o modelo recebe. Ao informar `--external-dir`, o GridSearch adiciona automaticamente fluxo, percentual de pesados, chuva, vento, visibilidade, obras, atributos de infraestrutura e calendário. Os dados meteorológicos observados são deslocados para o mês seguinte, para que a previsão não veja o clima do período que está tentando antecipar.

Os arquivos gerados são:

- `RoadFixerAPI/ModeloEstatistico/data/grid_search_report.json`: parâmetros escolhidos e métricas.
- `RoadFixerAPI/ModeloEstatistico/data/ranking_km_previsto.csv`: ranking previsto por km e mês.

## Dados que fazem diferença

Os dados existentes permitem começar com data, km, vítimas e tipo de acidente. Para um ranking que represente risco, e não apenas volume de registros, inclua também:

- exposição: fluxo por faixa/hora, percentual de pesados e velocidade média; sem ela, um km movimentado tende a parecer perigoso mesmo se sua taxa de acidente for normal;
- via: número e largura de faixas, curvas, aclives, acostamento, iluminação, limite de velocidade, interseções e obras;
- condições: chuva, visibilidade, vento, temperatura, dia da semana, feriados e horário;
- ocorrências operacionais: congestionamento, panes, animais na pista e intervenções anteriores;
- denominador e qualidade: extensão do segmento, período de cobertura, coordenadas e campos ausentes.

Não use como variável de entrada para prever o próximo mês a gravidade, vítimas ou causa do próprio acidente futuro: eles só podem ser usados como alvo histórico. Também é recomendável calibrar os pesos de severidade com a equipe de segurança viária e acompanhar diferenças por município e tipo de usuário da via.
