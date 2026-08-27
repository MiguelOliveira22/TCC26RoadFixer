from RoadFixerAPI.API.mapping.routes import assignRoutesAPI
import fastapi

server = fastapi.FastAPI()

assignRoutesAPI(server)