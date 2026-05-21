from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5435/cpe_calculator_db"
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    sendgrid_api_key: str = ""
    from_email: str = "noreply@pharmacist.com"
    frontend_url: str = "http://localhost:3003"
    env: str = "development"

    free_preview_hours: int = 3
    join_url: str = "https://www.pharmacist.com/join"
    member_cpe_url: str = "https://learn.pharmacist.com"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
