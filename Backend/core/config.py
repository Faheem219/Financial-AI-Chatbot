from pydantic import BaseSettings

class Settings(BaseSettings):
    # MongoDB configuration
    MONGO_URI: str
    MONGO_DB_NAME: str
    
    # HuggingFace API token for LLM & PDF processing
    HUGGINGFACE_USER_ACCESS_TOKEN: str
    
    # Free Finance API configuration (e.g., Alpha Vantage)
    FINANCE_API_KEY: str
    FINANCE_API_URL: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
