from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://neondb_owner:npg_jQlCFhNc31os@ep-steep-snow-a4dn6pvn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

    # Authentication
    BETTER_AUTH_SECRET: str = "your-secret-key-change-in-production"

    # Application
    DEBUG: bool = True
    PROJECT_NAME: str = "Todo API"
    VERSION: str = "1.0.0"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "https://*.vercel.app", "*"]

    # Qdrant Configuration
    QDRANT_URL: str = "https://8b21963a-7d0a-413a-915e-f58b2071a7b7.europe-west3-0.gcp.cloud.qdrant.io"
    QDRANT_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.i-1qWEAq8lrTZxJOLGbzmEXPkOX_r_OHf4KScQevMFg"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()