import os
import pathlib

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        extra = "allow"
        base_path = pathlib.Path(__file__).parent.parent.parent
        env_file = base_path / ".env" if os.getenv("ENV") != "production" else ".env.production"


settings = Settings()
