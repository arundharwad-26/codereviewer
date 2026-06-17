from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CodeReviewer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # GitHub
    GITHUB_WEBHOOK_SECRET: str
    GITHUB_TOKEN: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    # AI
    GEMINI_API_KEY: str

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()