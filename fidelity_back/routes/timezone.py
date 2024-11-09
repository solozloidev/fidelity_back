from auth.oauth2 import get_current_user
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.timezone import TimezoneCreate, TimezoneShow
from schemas.user import UserShow

from fidelity_back.config.database import db

router = APIRouter(prefix="/timezones", tags=["Timezone"])


projector = {"id": {"$toString": "$_id"}, "timezone": 1, "_id": 0}


@router.get("/", response_model=list[TimezoneShow], status_code=status.HTTP_200_OK)
async def get_timezones(current_user: UserShow = Depends(get_current_user)) -> list[TimezoneShow]:
    timezones = await db.timezones.find({}, projector).to_list(length=None)
    return timezones


@router.get("/{timezone_id}", response_model=TimezoneShow, status_code=status.HTTP_200_OK)
async def get_timezone(timezone_id: str, current_user: UserShow = Depends(get_current_user)) -> TimezoneShow:
    result = await db.timezones.find_one({"_id": ObjectId(timezone_id)}, projector)
    return result


@router.post("/", response_model=TimezoneShow, status_code=status.HTTP_201_CREATED)
async def create_timezone(
    new_timezone: TimezoneCreate, current_user: UserShow = Depends(get_current_user)
) -> TimezoneShow:
    check = await db.timezones.find_one({"timezone": new_timezone.timezone})
    if check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timezone already exists")

    result = await db.timezones.insert_one(new_timezone.model_dump())
    timezone = await db.timezones.find_one({"_id": result.inserted_id}, projector)
    return timezone
