from pydantic import BaseModel
from datetime import datetime


class MetricRead(BaseModel):
    id: int
    org: str
    date: datetime
    data: dict

    class Config:
        orm_mode = True
