from auth.hashing import Hash
from auth.oauth2 import get_current_user
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.user import UserCreate, UserShow, UserUpdate

from fidelity_back.config.database import db

router = APIRouter(prefix="/users", tags=["User"])


pipeline = [
    {
        "$lookup": {
            "from": "timezones",
            "localField": "current_timezone",
            "foreignField": "_id",
            "as": "current_timezone",
        }
    },
    {"$unwind": "$current_timezone"},
    {"$lookup": {"from": "user_roles", "localField": "roles", "foreignField": "_id", "as": "roles"}},
    {"$unwind": "$roles"},
    {
        "$group": {
            "_id": "$_id",
            "user_name": {"$first": "$user_name"},
            "is_active": {"$first": "$is_active"},
            "created_at": {"$first": "$created_at"},
            "updated_at": {"$first": "$updated_at"},
            "current_timezone": {"$first": "$current_timezone"},
            "roles": {"$push": "$roles"},
        }
    },
    {
        "$project": {
            "id": {"$toString": "$_id"},
            "_id": 0,
            "user_name": 1,
            "is_active": 1,
            "created_at": 1,
            "updated_at": 1,
            "current_timezone": {
                "id": {"$toString": "$current_timezone._id"},
                "timezone": "$current_timezone.timezone",
            },
            "roles": {
                "$map": {
                    "input": "$roles",
                    "as": "role",
                    "in": {"id": {"$toString": "$$role._id"}, "role": "$$role.role"},
                }
            },
        }
    },
]


@router.get("/", response_model=list[UserShow], status_code=status.HTTP_200_OK)
async def get_users(current_user: UserShow = Depends(get_current_user)) -> list[UserShow]:
    result = await db.users.aggregate(pipeline).to_list(None)
    return result


@router.get("/{user_id}", response_model=UserShow, status_code=status.HTTP_200_OK)
async def get_user(user_id: str, current_user: UserShow = Depends(get_current_user)) -> UserShow:
    result = await db.users.aggregate([{"$match": {"_id": ObjectId(user_id)}}, *pipeline]).next()
    return result


@router.post("/", response_model=UserShow, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreate, current_user: UserShow = Depends(get_current_user)) -> UserShow:
    check = await db.users.find_one({"user_name": new_user.user_name})
    if check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    new_user_data = serialize_user(new_user)
    result = await db.users.insert_one(new_user_data)
    user = await db.users.aggregate([{"$match": {"_id": result.inserted_id}}, *pipeline]).next()
    return user


@router.put("/{user_id}", response_model=UserShow, status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user: UserUpdate, current_user: UserShow = Depends(get_current_user)) -> UserShow:
    user_data = serialize_user(user)
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = await db.users.aggregate([{"$match": {"_id": ObjectId(user_id)}}, *pipeline]).next()
    return user


@router.delete("/{user_id}", response_model=UserShow, status_code=status.HTTP_200_OK)
async def delete_user(user_id: str, current_user: UserShow = Depends(get_current_user)) -> UserShow:
    user = await db.users.aggregate([{"$match": {"_id": ObjectId(user_id)}}, *pipeline]).next()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already inactive")

    user["is_active"] = False

    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_active": user["is_active"]}})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def serialize_user(user: UserCreate | UserUpdate) -> dict:
    user_data = user.model_dump()

    user_data["current_timezone"] = ObjectId(user.current_timezone)
    user_data["roles"] = [ObjectId(role) for role in user.roles]

    if isinstance(user, UserCreate):
        user_data["password"] = Hash.get_password_hash(user.password)

    return user_data
