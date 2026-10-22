# RoadFixerAPI

Backend do RoadFixer para coletar, processar e apresentar indicadores de
risco da Rodovia Anhanguera e do corredor associado à SP-330. O projeto tem
dois mecanismos de análise distintos:

1. **Índice heurístico de risco**: cálculo usado pela API e pelo frontend.
   Combina gravidade, tipo de acidente, chuva e recência para produzir um
   índice por quilômetro.
2. **Extra Trees temporal**: modelo de aprendizado de máquina que ordena os
   quilômetros por severidade esperada no período seguinte. Depois de cada
   atualização, ele gera a previsão consumida pelo endpoint `/predictionData`.

> O escopo deliberado do projeto inclui os acidentes da via principal, das
> marginais e dos acessos cujo identificador contém `330`. Portanto, os
> registros históricos processados não devem ser reduzidos a apenas `RODOVIA ==
> "SP330"`.

## Requisitos

- Python 3.11 ou superior (DuckDB 2.0).
- Node.js 20 ou superior, apenas para executar a interface React.
- Conexão com a internet para a atualização da ARTESP e a consulta do clima
  histórico no Open-Meteo.

## Executar pela primeira vez

Os comandos abaixo devem ser executados **na raiz do repositório**
`TCC26RoadFixer`.

### 1. Criar e ativar o ambiente Python

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r RoadFixerAPI/requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r RoadFixerAPI\requirements.txt
```

### 2. Iniciar a API

```bash
uvicorn RoadFixerAPI.API.main:server --reload --host 0.0.0.0 --port 8000
```

Verifique a inicialização em <http://127.0.0.1:8000/> e a documentação
interativa em <http://127.0.0.1:8000/docs>.

Ao iniciar, a API cria uma tarefa em segundo plano. Ela atualiza os dados da
ARTESP, recalcula o índice heurístico, treina o Extra Trees e volta a executar
diariamente às 23h50. A primeira execução pode demorar, pois consulta dados
externos e processa todos os arquivos históricos. Os logs aparecem no terminal
do Uvicorn.

### Armazenamento DuckDB

Na primeira inicialização, a API cria `RoadFixerAPI/data/roadfixer.duckdb`
e importa os JSONs de conteúdo, o índice de risco, a previsão existente,
os acidentes processados, o cache meteorológico e os pesos TAU. A importação
é transacional e acontece uma única vez por banco. Reiniciar a API preserva
os dados e não reaplica os arquivos antigos sobre as atualizações do banco.

Para preparar o banco sem iniciar o servidor:

```bash
python -m RoadFixerAPI.database
```

Todas as rotas consultam DuckDB. A atualização da ARTESP substitui somente
os acidentes do ano atualizado, o cálculo heurístico grava o clima e o risco
no banco, e o Extra Trees publica a previsão no banco. Os formatos HTTP
continuam compatíveis com o frontend.

Os CSVs e JSONs versionados servem para a importação inicial. Os downloads
brutos da ARTESP, os arquivos contextuais externos e as exportações do modelo
continuam sendo arquivos de entrada ou de análise. Editar um arquivo legado
depois da migração não altera o banco. Faça backup do `.duckdb` com a API
parada; o arquivo local e seu WAL são ignorados pelo Git.

Configurações opcionais por variável de ambiente:

| Variável | Padrão | Uso |
| --- | --- | --- |
| `ROADFIXER_DB_PATH` | `RoadFixerAPI/data/roadfixer.duckdb` | Caminho do banco. O padrão independe do diretório do terminal; um caminho personalizado relativo parte do diretório atual. |
| `ROADFIXER_AUTO_UPDATE` | `1` | Use `0` para servir os dados sem iniciar downloads e treinamento automáticos. |

Execute uma única instância da API, com um worker. As rotas e o agendador
compartilham o banco no mesmo processo, com conexões protegidas por trava e
transações. Pare a API antes de executar uma atualização manual que grave no
mesmo banco. Essa configuração segue o modelo de concorrência do
[DuckDB](https://duckdb.org/docs/stable/connect/concurrency).

Tabelas principais: `accidents` e `weather` (separadas por `source_file`),
`tau`, `risk_values`, `predictions` e `documents` (conteúdo JSON e metadados).
`GET /datasets/` monta o download JSON a partir do banco.

### 3. Iniciar o frontend opcionalmente

Em outro terminal, ainda na raiz:

```bash
npm --prefix RoadFixer install
npm --prefix RoadFixer run dev
```

A interface usa `http://127.0.0.1:8000/`, definido em
`RoadFixer/src/Constants.js`. Mantenha a API na porta 8000 ou altere esse
valor no frontend.

## Como o índice de risco da API funciona

O fluxo executado pela API é:

```text
ARTESP
  -> data/accidents/non_Processed/<ano>.csv
  -> normalização e recorte do corredor SP-330
  -> DuckDB: accidents (ano atualizado)
       -> cálculo de gravidade, tau, chuva e recência
       -> DuckDB: weather + risk_values
       -> GET /riskData -> gráfico de índice histórico
       -> Extra Trees temporal
       -> DuckDB: predictions (com exportação CSV para análise)
       -> GET /predictionData -> gráfico de previsão
```

Para cada acidente, o cálculo faz o seguinte:

- dá pesos maiores para vítimas fatais e graves;
- aplica o valor `TAU` correspondente à classe e subclasse do acidente;
- usa dados de chuva, vento e rajada em cache ou solicita o histórico ao
  Open-Meteo;
- aumenta o multiplicador de risco com chuva: de `1.0` em dia seco até `1.5`
  para chuva de 20 mm ou mais;
- reduz gradualmente o peso de acidentes mais antigos;
- agrega os resultados por km e os normaliza em uma escala aproximada de 0 a
  10.

O resultado é **um índice histórico priorizado**, não uma confirmação de risco
em tempo real e nem uma previsão de acidentes futuros. A disponibilidade e a
qualidade do clima histórico podem afetar o cálculo.

## Executar a IA de Extra Trees manualmente

O modelo de aprendizado de máquina recebe o histórico do DuckDB por km e mês. Para cada
período, as variáveis de acidentes dos últimos 30, 90 e 365 dias são usadas
para estimar a severidade do mês seguinte. A validação é temporal: anos e
meses futuros não entram no treinamento dos períodos anteriores.

Normalmente o agendador executa o modelo após atualizar os dados. Para gerar
ou reproduzir o resultado manualmente, execute:

```bash
python -m RoadFixerAPI.ModeloEstatistico.grid_search
```

No Windows PowerShell, use uma única linha:

```powershell
python -m RoadFixerAPI.ModeloEstatistico.grid_search
```

O comando gera dois arquivos:

- `data_tau/grid_search_report.json`: parâmetros escolhidos, métricas e
  variáveis usadas;
- `data_tau/ranking_km_previsto.csv`: ranking de km e risco previsto para a
  avaliação histórica do último ano;
- `data_tau/previsao_proximo_mes.csv`: exportação do ranking sem alvo conhecido para
  análise. A API consulta a previsão publicada no DuckDB.

O Extra Trees carrega automaticamente as contagens diárias e os arquivos de
infraestrutura na pasta `data_tau/external/raw`. Arquivos opcionais
`traffic.csv`, `weather.csv`, `speed.csv`, `works.csv` e `infrastructure.csv`
podem acrescentar contexto. O contrato de cada CSV está em
`data_tau/external/README.md`.

> O comando acima sobrescreve os artefatos de relatório e ranking e publica
> a previsão no DuckDB quando usa o caminho de saída padrão. Com `--output`
> personalizado, somente os artefatos de análise são gerados. O argumento
> `--data-dir` permite usar CSVs externos para experimentos.

## Rotas HTTP

| Método | Rota | Retorno |
| --- | --- | --- |
| GET | `/` | Texto simples de confirmação do servidor. |
| GET | `/carddata/` | Cards da página inicial. |
| GET | `/statsdata/` | Conteúdo estático de estatísticas. |
| GET | `/accidentHistory` | Registros apresentados como histórico pela interface. |
| GET | `/riskData` | Índices armazenados no DuckDB. Retorna uma estrutura vazia segura se o índice ainda não foi gerado. |
| GET | `/predictionData` | Ranking do próximo mês do Extra Trees, lido do DuckDB. Retorna uma estrutura vazia segura enquanto o modelo não terminar. |
| GET | `/listadatasets/` | Lista de conjuntos apresentados na interface. |
| GET | `/datasets/` | Download do JSON de conjuntos. |

Exemplo de resposta de `/riskData`:

```json
{
  "last_update": "2026-10-08",
  "risk": [0.0, 2.15, 4.73]
}
```

Cada posição da lista `risk` representa o km cujo número é o próprio índice.

## Arquivo por arquivo

### Inicialização e API

| Arquivo | Responsabilidade |
| --- | --- |
| `database.py` | Cria o DuckDB, importa os arquivos legados uma vez e centraliza consultas e gravações transacionais. |
| `API/main.py` | Cria o `FastAPI`, libera CORS para desenvolvimento, registra as rotas e inicia/cancela o agendador no ciclo de vida da aplicação. |
| `API/README.md` | Documento inicial e resumido da API. Este README central é a referência atual de instalação e execução. |
| `API/mapping/routes.py` | Define as rotas de saúde, cards, estatísticas, histórico, risco e previsão. `/riskData` e `/predictionData` consultam DuckDB; ambas possuem fallback seguro. |
| `API/mapping/directory.py` | Lista os conjuntos e gera o download JSON a partir do DuckDB. |
| `API/__init__.py` e `API/mapping/__init__.py` | Marcam os diretórios como pacotes Python. |
| `API/content/cards/content.json` | Conteúdo inicial dos cards, importado no DuckDB. |
| `API/content/stats/content.json` | Conteúdo inicial de estatísticas, importado no DuckDB. |
| `API/content/conjuntos/content.json` | Lista inicial de conjuntos, importada no DuckDB. |
| `API/content/accident-history/content.json` | Histórico demonstrativo inicial, importado no DuckDB. |
| `API/content/accident-history/risk/savedData.json` | Índice heurístico legado; importado uma vez no DuckDB. |
| `API/content/accident-history/risk/testeSalvo.json` | Artefato de teste antigo. Não é mais usado pela rota de risco. |

### Atualização e preparação dos dados

| Arquivo | Responsabilidade |
| --- | --- |
| `ProcessamentoParametros/updateData.py` | Cria diretórios, baixa o CSV anual da ARTESP, normaliza classe/subclasse, expande os veículos, preserva o corredor SP-330 com acessos e agenda a atualização diária. Depois, chama o cálculo de risco e a previsão Extra Trees. |
| `ProcessamentoParametros/main.ipynb` | Notebook exploratório de tratamento de parâmetros; não é executado pela API. |
| `ProcessamentoParametros/search-files-weather.ipynb` | Notebook exploratório para investigar arquivos meteorológicos; não é executado pela API. |
| `ProcessamentoParametros/__init__.py` | Marcador de pacote Python. |
| `data/accidents/non_Processed/<ano>.csv` | Download bruto anual da ARTESP. |
| `data/accidents/processed/p<ano>.csv` | Histórico legado importado uma vez em `accidents`, mantendo via, marginais e acessos do corredor. |
| `data/weather-data/p<ano>.csv` | Cache legado importado uma vez em `weather`, evitando consultas repetidas ao Open-Meteo. |

### Índice heurístico de risco

| Arquivo | Responsabilidade |
| --- | --- |
| `ModeloEstatistico/core/riskCalculations.py` | Lê acidentes, clima e TAU do DuckDB, calcula gravidade, chuva e recência, e grava o índice no banco. |
| `ModeloEstatistico/data_tau/tau.csv` | Tabela inicial de pesos por classe e subclasse, importada em `tau`. |
| `ModeloEstatistico/core/__init__.py` | Marcador de pacote Python. |

### Experimento de aprendizado de máquina

| Arquivo | Responsabilidade |
| --- | --- |
| `ModeloEstatistico/grid_search.py` | Constrói o painel km/mês, cria variáveis históricas sem vazamento do alvo, executa `ExtraTreesRegressor`, faz validação temporal e gera relatório, ranking de avaliação e previsão do próximo mês. |
| `ModeloEstatistico/context_features.py` | Carrega e normaliza variáveis externas: fluxo, pesados, chuva, vento, velocidade, obras, geometria, acessos e calendário. Fluxo observado é deslocado para o mês seguinte para não vazar o alvo. |
| `ModeloEstatistico/data_tau/grid_search_report.json` | Resultado mais recente da busca de parâmetros do Extra Trees. |
| `ModeloEstatistico/data_tau/ranking_km_previsto.csv` | Ranking gerado pelo modelo para avaliação. |
| `ModeloEstatistico/data_tau/previsao_proximo_mes.csv` | Exportação para análise e carga inicial; as previsões novas são publicadas no DuckDB. |
| `ModeloEstatistico/data_tau/external/README.md` | Contrato e exemplos de dados contextuais externos. |
| `ModeloEstatistico/data_tau/external/*.example` | Modelos de CSV para infraestrutura, tráfego, velocidade e obras. |
| `ModeloEstatistico/data_tau/external/raw/contagem_diaria_*.csv` | Contagens diárias da ARTESP, usadas como fluxo e proporção de pesados. |
| `ModeloEstatistico/data_tau/external/raw/cci_malha_rodoviaria_sp.xlsx` | Cadastro de malha, usado para atributos de pista. |
| `ModeloEstatistico/data_tau/external/raw/acessos_rodoviarios.xlsx` | Cadastro de acessos, usado para densidade e condição dos acessos. |
| `ModeloEstatistico/GRID_SEARCH.md` | Nota histórica do experimento; prefira os comandos deste README, pois eles usam os caminhos atuais do repositório. |
| `ModeloEstatistico/README.md` | Exemplo de estrutura de resposta do Open-Meteo. |
| `ModeloEstatistico/__init__.py` | Marcador de pacote Python. |

### Módulo não integrado

| Arquivo | Situação |
| --- | --- |
| `ModeloResolucao/main.py` | Vazio; não é iniciado nem usado pela API. |
| `ModeloResolucao/mapping/routes.py` | Protótipo com rotas sem implementação completa; não é registrado em `API/main.py`. |
| `ModeloResolucao/__init__.py` e `ModeloResolucao/mapping/__init__.py` | Marcadores de pacote. |

### Dependências

| Arquivo | Responsabilidade |
| --- | --- |
| `requirements.txt` | Dependências Python do backend, incluindo DuckDB, FastAPI, Pandas, Requests, GeoPandas, PyTorch e `scikit-learn`, necessário para o Extra Trees. |

## Verificações rápidas

Com a API em execução:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/riskData
```

Para validar o frontend:

```bash
npm --prefix RoadFixer run lint
npm --prefix RoadFixer run build
```

Para validar a migração, as rotas e as atualizações sem acessar serviços externos:

```bash
python -m unittest discover -s RoadFixerAPI/tests -v
```

## Limites conhecidos

- O índice no DuckDB é atualizado após uma execução bem-sucedida do cálculo
  de risco. Sem dados importados ou calculados, a rota retorna o fallback vazio.
- A atualização automática depende de ARTESP e Open-Meteo estarem
  disponíveis.
- O Extra Trees gera uma previsão separada em `/predictionData`; ela não deve
  ser misturada numericamente com o índice heurístico de `/riskData`.
- O índice heurístico não deve ser divulgado como previsão operacional ou
  risco em tempo real sem validação de segurança viária e calibração com dados
  de exposição ao tráfego.
