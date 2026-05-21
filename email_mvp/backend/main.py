from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from backend.db.base import Base
from backend.db.session import engine, SessionLocal
from backend.db.models import member, email_send, email_event  # noqa: F401 — registers models
from backend.api.routes import members, emails, analytics
from backend.utils.seed_data import seed_members
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title="APhA Personalized Member Value Email API",
    version="1.0.0",
    description="Monthly personalized benefit-value email generation and delivery system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router)
app.include_router(emails.router)
app.include_router(analytics.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_members(db, count=200)
        logger.info("Database seeded with 200 members")
    finally:
        db.close()

    if settings.env != "test":
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            _run_scheduled_job,
            "cron",
            day=settings.email_send_day,
            hour=settings.email_send_hour,
            id="monthly_email_job",
        )
        scheduler.start()
        logger.info(f"Scheduler started: day={settings.email_send_day} hour={settings.email_send_hour}")


def _run_scheduled_job():
    db = SessionLocal()
    try:
        from backend.scheduler.monthly_job import run_monthly_email_job
        results = run_monthly_email_job(db)
        logger.info(f"Scheduled job complete: {results}")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "email-mvp"}
