from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5436/crosssell_db"
    redis_url: str = "redis://localhost:6380/0"
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    smtp_host: str = "smtp.postmarkapp.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = "membership@pharmacist.com"
    secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    mlflow_tracking_uri: str = "./mlruns"
    env: str = "development"

    min_expansion_score_to_nudge: float = 60.0
    max_nudges_per_member_per_month: int = 2
    nudge_cooldown_days: int = 14

    products: list = ["education", "publications", "events", "career", "advocacy"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
