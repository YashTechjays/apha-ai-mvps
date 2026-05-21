from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5433/concierge_db"
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    chroma_persist_dir: str = "./chroma_store"
    hubspot_api_key: str = ""
    personify_api_key: str = ""
    env: str = "development"

    max_conversation_turns: int = 20
    lead_capture_after_turns: int = 3
    inactivity_timeout_minutes: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
