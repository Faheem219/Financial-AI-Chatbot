# Backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    HUGGINGFACE_USER_ACCESS_TOKEN: str
    FINANCE_API_KEY: str
    FINANCE_API_URL: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
