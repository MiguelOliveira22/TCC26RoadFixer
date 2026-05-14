import fastapi

server = fastapi.FastAPI()

@server.get("/")
async def baseExec():
    return "YES"