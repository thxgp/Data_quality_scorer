from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/postgres"

    # API Keys
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "DataQualityScorer/0.1"
    
    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = None

    # Quality Parameters
    QUALITY_THRESHOLD: float = 70.0
    CHECK_INTERVAL_HOURS: int = 1

    # App Settings
    PROJECT_NAME: str = "Data Quality Scorer"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
