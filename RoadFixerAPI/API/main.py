import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
import os
from fastapi.middleware.cors import CORSMiddleware

from RoadFixerAPI.database import get_database
from RoadFixerAPI.API.mapping.directory import assignRoutesDirectory
from RoadFixerAPI.API.mapping.routes import assignRoutesAPI
from RoadFixerAPI.ProcessamentoParametros.updateData import iniciarAtualizacao

@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(get_database().initialize)
    tarefa = iniciarAtualizacao() if os.environ.get("ROADFIXER_AUTO_UPDATE", "1") != "0" else None
    try:
        yield
    finally:
        if tarefa is not None:
            tarefa.cancel()
            try:
                await tarefa
            except asyncio.CancelledError:
                pass

server = FastAPI(
    lifespan=lifespan
)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


assignRoutesAPI(server)
assignRoutesDirectory(server)