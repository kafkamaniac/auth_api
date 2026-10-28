#Настройки приложения и подключение к базе данных PostgreSQL.

from peewee import PostgresqlDatabase
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):    
    """Хранит настройки приложения, загружаемые из файла .env."""
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
settings = Settings()
    
db = PostgresqlDatabase(
    settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT
    )
    