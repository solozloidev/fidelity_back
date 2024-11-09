from pydantic import BaseModel


class UserRoleCreate(BaseModel):
    role: str


class UserRoleShow(BaseModel):
    id: str
    role: str
