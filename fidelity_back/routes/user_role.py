from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from schemas.user_role import UserRoleCreate, UserRoleShow

from fidelity_back.config.database import db

router = APIRouter(prefix="/user_roles", tags=["User"])


projector = {"id": {"$toString": "$_id"}, "role": 1, "_id": 0}


@router.get("/", response_model=list[UserRoleShow], status_code=status.HTTP_200_OK)
async def get_user_roles() -> list[UserRoleShow]:
    result = await db.user_roles.find({}, projector).to_list(length=20)

    return result


@router.get("/{user_role_id}", response_model=UserRoleShow, status_code=status.HTTP_200_OK)
async def get_user_role(user_role_id: str) -> UserRoleShow:
    result = await db.user_roles.find_one({"_id": ObjectId(user_role_id)}, projector)
    return result


@router.post("/", response_model=UserRoleShow, status_code=status.HTTP_201_CREATED)
async def create_user_role(new_user_role: UserRoleCreate) -> UserRoleShow:
    check = await db.user_roles.find_one({"role": new_user_role.role})
    if check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User role already exists")
    result = await db.user_roles.insert_one(new_user_role.model_dump())
    user_role = await db.user_roles.find_one({"_id": result.inserted_id}, projector)
    return user_role
