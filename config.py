from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200
    REDIS_HOST: str
    REDIS_PORT: int
    ADMIN_SECRET_KEY: str
    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: str
    ADMIN_NAME: str
    MODE: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Settings()
