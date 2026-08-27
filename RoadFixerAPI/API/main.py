from RoadFixerAPI.API.mapping.directory import assignRoutesDirectory
from RoadFixerAPI.API.mapping.routes import assignRoutesAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

server = FastAPI()

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

assignRoutesAPI(server)
assignRoutesDirectory(server)