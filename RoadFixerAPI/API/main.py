import sys
from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware

from RoadFixerAPI.API.mapping.routes import assignRoutes
from RoadFixerAPI.API.update.updateData import iniciarAtualizacao

@asynccontextmanager
async def lifespan(app: FastAPI):
    tarefa = iniciarAtualizacao()
    yield tarefa.cancel()

    try:
        await tarefa
    except asyncio.CancelledError:
        print("Atualização dos Dados Concluida!")

server = FastAPI(lifespan=lifespan)
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

assignRoutes(server)