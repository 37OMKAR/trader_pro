"""
Market AI — API Configuration
Zero-dependency settings using standard os.environ and Pydantic.
"""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Market AI — Indian Market Intelligence Platform")
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./market_ai.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ]
    DATA_PROVIDER: str = os.getenv("DATA_PROVIDER", "development")


settings = Settings()
