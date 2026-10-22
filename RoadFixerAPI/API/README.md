# RoadFixerAPI

A API FastAPI usa DuckDB para conteúdo, acidentes, clima, risco e previsão.
A primeira inicialização cria o banco e importa os arquivos legados.

Na raiz do repositório:

```bash
python -m pip install -r RoadFixerAPI/requirements.txt
uvicorn RoadFixerAPI.API.main:server --reload --host 0.0.0.0 --port 8000
```

Consulte o [README do backend](../README.md) para configuração do banco,
agendador, rotas e verificações. A documentação interativa fica em
<http://127.0.0.1:8000/docs>.
