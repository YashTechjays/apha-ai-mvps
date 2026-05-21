from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5434/email_db"
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    openai_subject_model_name: str = "gpt-4o-mini"
    sendgrid_api_key: str = ""
    from_email: str = "noreply@pharmacist.com"
    from_name: str = "APhA Membership Team"
    env: str = "development"

    max_tokens_per_email: int = 500
    email_send_day: int = 1
    email_send_hour: int = 9
    pilot_batch_size: int = 50

    cpe_credit_value_usd: float = 25.0
    annual_meeting_value_usd: float = 350.0
    webinar_value_usd: float = 50.0
    journal_monthly_value_usd: float = 30.0
    pharmacylibrary_monthly_value_usd: float = 20.0

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
