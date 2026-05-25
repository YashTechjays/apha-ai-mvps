from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import prospects, campaigns, webhooks, analytics, auth
from db.base import Base
from db.session import engine
from utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA AI Outreach Automation API",
    description="AI-powered prospect identification and personalized email outreach",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3007", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prospects.router)
app.include_router(campaigns.router)
app.include_router(webhooks.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    from db.session import SessionLocal
    from db.models.prospect import Prospect
    from utils.seed_data import generate_mock_prospects

    db = SessionLocal()
    try:
        if db.query(Prospect).count() == 0:
            logger.info("Seeding 300 mock prospects...")
            from pipeline.npi_importer import run_npi_import
            run_npi_import(db, use_mock=True, max_per_state=100)
    finally:
        db.close()
    logger.info("Outreach Automation API ready.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-outreach-automation"}
