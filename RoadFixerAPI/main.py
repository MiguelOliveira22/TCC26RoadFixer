from RoadFixerAPI.mapping.routes import assignRoutesAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

server = FastAPI()

server.add_middleware(CORSMiddleware, allow_origins=["*"])

assignRoutesAPI(server)