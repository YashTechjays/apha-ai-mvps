from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://apha:apha_secret@localhost:5441/rfp_graph_db"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "apha_secret"
    redis_url: str = "redis://localhost:6384/0"
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    embedding_model_name: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    firecrawl_api_key: str = ""
    secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    crawl_interval_hours: int = 24
    max_pages_per_crawl: int = 50
    env: str = "development"
    smtp_host: str = "smtp.postmarkapp.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@apha.org"
    frontend_url: str = "http://localhost:3009"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
