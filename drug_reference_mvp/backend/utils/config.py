from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5437/drug_ref_db"
    redis_url: str = "redis://localhost:6381/0"
    env: str = "development"

    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    chroma_persist_dir: str = "./chroma_store"
    chroma_collection_name: str = "apha_drug_reference"
    rag_top_k: int = 6
    rag_min_score: float = 0.3
    max_answer_tokens: int = 1200

    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""

    rate_limit_individual: int = 50
    rate_limit_team: int = 200
    rate_limit_institution: int = 1000
    rate_limit_enterprise: int = 10000
    rate_limit_trial: int = 10

    frontend_url: str = "http://localhost:3005"
    join_url: str = "https://www.pharmacist.com/join"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Module-level singleton for direct import: `from backend.utils.config import settings`
settings = get_settings()
