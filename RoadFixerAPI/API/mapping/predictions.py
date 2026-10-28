from contextlib import asynccontextmanager
from pathlib import Path

from joblib import Parallel, delayed
import joblib

from fastapi import FastAPI, HTTPException

BASE_MODEL_PATH = Path("")
modelo: <TYPE> = None

class ModelException(RuntimeError):
    pass

@asynccontextmanager
async def carregarModelo(api: FastAPI):
    global modelo

    try:
        modelo = joblib.load(BASE_MODEL_PATH)
    except:
        raise ModelException(f"Modelo Não Encontrado.")

def assignPredictionModel(api: FastAPI):
    @api.get()
    async def c():
        pass

    @api.post()
    async def d():
        pass
