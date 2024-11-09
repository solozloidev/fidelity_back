from pydantic import BaseModel


class TimezoneCreate(BaseModel):
    timezone: str


class TimezoneShow(BaseModel):
    id: str
    timezone: str
