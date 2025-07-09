from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    OPENWEATHER_API_KEY: str
    GOOGLE_PROJECT_ID: Optional[str] = None
    REDIS_DSN: str = "redis://localhost:6379/0"

settings = Settings()
