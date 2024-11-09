from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings

MONGO_URI = f"mongodb://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}"

client = AsyncIOMotorClient(MONGO_URI)
db = client[settings.DB_NAME]
