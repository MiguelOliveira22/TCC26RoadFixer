import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .mapping.predictions import ForecastModelError, assignPredictionModel, forecast_service
from .mapping.routes import assignRoutes
from .update.updateData import iniciarAtualizacao


def _auto_update_enabled() -> bool:
    return os.getenv("ROADFIXER_AUTO_UPDATE", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    tarefa = None

    try:
        forecast_service.load()
        print("[IA] Modelos SARIMAX e ARIMAX carregados com sucesso.")
    except ForecastModelError as error:
        # A API permanece disponível para as demais rotas e informa 503 nas
        # rotas de IA até que os artefatos sejam disponibilizados/recarregados.
        print(f"[IA] Modelos de previsão indisponíveis: {error}")

    if _auto_update_enabled():
        tarefa = iniciarAtualizacao()

    try:
        yield
    finally:
        if tarefa is not None:
            tarefa.cancel()

            try:
                await tarefa
            except asyncio.CancelledError:
                print("Atualização dos Dados Concluída/Cancelada!")

server = FastAPI(
    title="RoadFixer API",
    description="Dados rodoviários e previsões encadeadas de tráfego e acidentes.",
    lifespan=lifespan,
)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

assignRoutes(server)
assignPredictionModel(server)
