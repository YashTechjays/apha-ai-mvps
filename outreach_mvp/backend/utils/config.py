from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Core
    database_url: str = "postgresql://apha:apha_secret@localhost:5439/outreach_db"
    redis_url: str = "redis://localhost:6383/0"
    secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    env: str = "development"

    # AI
    anthropic_api_key: str = ""
    mlflow_tracking_uri: str = "./mlruns"

    # Email delivery
    sendgrid_api_key: str = ""
    sendgrid_webhook_secret: str = ""
    from_email: str = "membership@pharmacist.com"
    from_name: str = "APhA Membership Team"
    physical_address: str = "2215 Constitution Ave NW, Washington, DC 20037"

    # Sending rate limits
    max_sends_per_hour: int = 200
    max_sends_per_day: int = 2000
    send_window_start_hour: int = 9
    send_window_end_hour: int = 17

    # ICP scoring
    min_icp_score_to_contact: float = 60.0

    # APhA URLs
    join_url: str = "https://www.pharmacist.com/join"
    unsubscribe_url: str = "https://www.pharmacist.com/unsubscribe"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
