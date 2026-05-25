from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5438/acquisition_db"
    redis_url: str = "redis://localhost:6382/0"
    anthropic_api_key: str = ""
    sendgrid_api_key: str = ""
    from_email: str = "hello@pharmacist.com"
    frontend_url: str = "http://localhost:3006"
    env: str = "development"

    # Freemium limits per IP per day
    salary_free_checks_per_day: int = 3
    interaction_free_checks_per_day: int = 3
    career_free_assessments_per_day: int = 1

    # APhA join URL
    join_url: str = "https://www.pharmacist.com/join"
    member_benefit_url: str = "https://www.pharmacist.com/membership"

    model_config = {"env_file": ".env"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
