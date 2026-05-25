from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://apha:apha_secret@postgres:5432/apha_master_db"

    # Auth (shared across churn, crosssell, drug_ref)
    secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # OpenAI (concierge, cpe, crosssell, drug_ref, email)
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"

    # SMTP (email, cpe, crosssell)
    smtp_host: str = "smtp.postmarkapp.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@pharmacist.com"
    from_name: str = "APhA Membership Team"

    # Churn-specific
    mlflow_tracking_uri: str = "./mlruns"
    aws_s3_bucket: str = "apha-churn-models"
    aws_region: str = "us-east-1"

    # Concierge-specific
    chroma_persist_dir: str = "./chroma_store"
    hubspot_api_key: str = ""
    personify_api_key: str = ""
    max_conversation_turns: int = 20
    lead_capture_after_turns: int = 3
    inactivity_timeout_minutes: int = 30

    # CPE-specific
    frontend_url: str = "http://localhost:3100"
    free_preview_hours: int = 3
    join_url: str = "https://www.pharmacist.com/join"
    member_cpe_url: str = "https://learn.pharmacist.com"

    # CrossSell-specific
    redis_url: str = "redis://redis:6379/0"
    min_expansion_score_to_nudge: float = 60.0
    max_nudges_per_member_per_month: int = 2
    nudge_cooldown_days: int = 14
    products: list = ["education", "publications", "events", "career", "advocacy"]

    # Drug Ref-specific
    jwt_secret: str = "dev-secret"
    chroma_collection_name: str = "apha_drug_reference"
    rag_top_k: int = 6
    rag_min_score: float = 0.3
    max_answer_tokens: int = 1200
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""
    rate_limit_individual: int = 50
    rate_limit_team: int = 200
    rate_limit_institution: int = 1000
    rate_limit_enterprise: int = 10000
    rate_limit_trial: int = 10

    # Email-specific
    openai_subject_model_name: str = "gpt-4o-mini"
    max_tokens_per_email: int = 500
    email_send_day: int = 1
    email_send_hour: int = 9
    pilot_batch_size: int = 50
    cpe_credit_value_usd: float = 25.0
    annual_meeting_value_usd: float = 350.0
    webinar_value_usd: float = 50.0
    journal_monthly_value_usd: float = 30.0
    pharmacylibrary_monthly_value_usd: float = 20.0

    # Acquisition Funnels
    anthropic_api_key: str = ""
    acq_salary_free_checks_per_day: int = 3
    acq_interaction_free_checks_per_day: int = 3
    acq_career_free_assessments_per_day: int = 1

    # Outreach Automation
    sendgrid_api_key: str = ""
    sendgrid_webhook_secret: str = ""
    physical_address: str = "2215 Constitution Ave NW, Washington, DC 20037"
    max_sends_per_hour: int = 200
    max_sends_per_day: int = 2000
    send_window_start_hour: int = 9
    send_window_end_hour: int = 17
    min_icp_score_to_contact: float = 60.0
    unsubscribe_url: str = "https://www.pharmacist.com/unsubscribe"

    env: str = "development"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
