import json

from fastapi import FastAPI
from fastapi.responses import Response

from RoadFixerAPI.database import get_database

def assignRoutesDirectory(api: FastAPI):

    @api.get("/listadatasets/")
    def listDatasets():
        return get_database().get_document("datasets")

    @api.get("/datasets/")
    def sendDataset() -> Response:
        content = get_database().get_document("datasets")
        return Response(
            content=json.dumps(content, ensure_ascii=False).encode("utf-8"),
            media_type="application/octet-stream",
            headers={"Content-Disposition": 'attachment; filename="content.json"'},
        )