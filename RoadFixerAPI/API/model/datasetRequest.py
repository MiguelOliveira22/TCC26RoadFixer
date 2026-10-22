from pydantic import BaseModel

class DatasetRequest(BaseModel):
    dataset_name: str
