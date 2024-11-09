from datetime import datetime

from pydantic import BaseModel
from schemas.timezone import TimezoneShow
from schemas.user_role import UserRoleShow


class UserCreate(BaseModel):
    user_name: str
    password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    current_timezone: str  # timezone id
    roles: list[str]  # list user roles ids


class UserUpdate(BaseModel):
    id: str
    user_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    current_timezone: str  # timezone id
    roles: list[str]  # list user roles ids


class UserShow(BaseModel):
    id: str
    user_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    current_timezone: TimezoneShow  # timezone object
    roles: list[UserRoleShow]  # list user roles ids


class UserFullShow(UserShow):
    password: str
