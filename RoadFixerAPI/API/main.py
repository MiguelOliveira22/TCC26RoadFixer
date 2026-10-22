from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
import os
from fastapi.middleware.cors import CORSMiddleware

from RoadFixerAPI.database import get_database
from RoadFixerAPI.API.mapping.directory import assignRoutesDirectory
from RoadFixerAPI.API.mapping.routes import assignRoutes
from RoadFixerAPI.ProcessamentoParametros.updateData import iniciarAtualizacao

@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(get_database().initialize)
    tarefa = iniciarAtualizacao() if os.environ.get("ROADFIXER_AUTO_UPDATE", "1") != "0" else None
    try:
        await tarefa
    except asyncio.CancelledError:
        print("Atualização dos Dados Concluída/Cancelada!")

server = FastAPI(lifespan=lifespan)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

assignRoutes(server)