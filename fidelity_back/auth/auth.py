from auth import oauth2
from auth.hashing import Hash
from bson import ObjectId
from config.database import db
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(prefix="", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=dict)
async def login(request: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = await db.users.find_one({"user_name": request.username})
    if not user or not Hash.verify_hash(request.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    is_admin = False
    for role in user["roles"]:
        result = await db.user_roles.find_one({"_id": ObjectId(role)})
        if result["role"] == "admin":
            is_admin = True
            break
    access_token = oauth2.create_access_token(data={"user_name": user["user_name"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user["user_name"],
        "id": str(user["_id"]),
        "is_admin": is_admin,
    }
