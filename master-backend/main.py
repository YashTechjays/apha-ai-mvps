"""
APhA AI Master Backend — Unified API serving all 8 MVPs.

Route prefixes:
  /api/churn/*        — Churn Prediction
  /api/concierge/*    — Membership Concierge
  /api/cpe/*          — CPE Gap Calculator
  /api/crosssell/*    — Cross-Sell Engine
  /api/drugref/*      — Drug Reference Tool
  /api/email/*        — Personalized Value Email
  /api/acquisition/*  — Public Acquisition Funnels
  /api/outreach/*     — AI Outreach Automation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine, SessionLocal
from core.logger import get_logger
from core.config import get_settings

logger = get_logger("master")
settings = get_settings()

app = FastAPI(
    title="APhA AI Master API",
    description="Unified API for all 8 APhA AI MVPs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Churn Prediction routes ──────────────────────────────────────────
from apps.churn.api.routes import auth as churn_auth
from apps.churn.api.routes import members as churn_members
from apps.churn.api.routes import scores as churn_scores
from apps.churn.api.routes import alerts as churn_alerts

app.include_router(churn_auth.router, prefix="/api/churn")
app.include_router(churn_members.router, prefix="/api/churn")
app.include_router(churn_scores.router, prefix="/api/churn")
app.include_router(churn_alerts.router, prefix="/api/churn")

# ── Concierge routes ────────────────────────────────────────────────
from apps.concierge.api.routes import chat as concierge_chat
from apps.concierge.api.routes import leads as concierge_leads
from apps.concierge.api.routes import analytics as concierge_analytics

app.include_router(concierge_chat.router, prefix="/api/concierge")
app.include_router(concierge_leads.router, prefix="/api/concierge")
app.include_router(concierge_analytics.router, prefix="/api/concierge")

# ── CPE Calculator routes ──────────────────────────────────────────
from apps.cpe.api.routes import calculator as cpe_calculator
from apps.cpe.api.routes import leads as cpe_leads
from apps.cpe.api.routes import analytics as cpe_analytics

app.include_router(cpe_calculator.router, prefix="/api/cpe")
app.include_router(cpe_leads.router, prefix="/api/cpe")
app.include_router(cpe_analytics.router, prefix="/api/cpe")

# ── Cross-Sell Engine routes ────────────────────────────────────────
from apps.crosssell.api.routes import auth as crosssell_auth
from apps.crosssell.api.routes import scores as crosssell_scores
from apps.crosssell.api.routes import nudges as crosssell_nudges
from apps.crosssell.api.routes import banners as crosssell_banners
from apps.crosssell.api.routes import analytics as crosssell_analytics

app.include_router(crosssell_auth.router, prefix="/api/crosssell")
app.include_router(crosssell_scores.router, prefix="/api/crosssell")
app.include_router(crosssell_nudges.router, prefix="/api/crosssell")
app.include_router(crosssell_banners.router, prefix="/api/crosssell")
app.include_router(crosssell_analytics.router, prefix="/api/crosssell")

# ── Drug Reference routes ──────────────────────────────────────────
from apps.drug_ref.api.routes import auth as drugref_auth
from apps.drug_ref.api.routes import query as drugref_query
from apps.drug_ref.api.routes import subscriptions as drugref_subscriptions
from apps.drug_ref.api.routes import webhooks as drugref_webhooks
from apps.drug_ref.api.routes import analytics as drugref_analytics

app.include_router(drugref_auth.router, prefix="/api/drugref")
app.include_router(drugref_query.router, prefix="/api/drugref")
app.include_router(drugref_subscriptions.router, prefix="/api/drugref")
app.include_router(drugref_webhooks.router, prefix="/api/drugref")
app.include_router(drugref_analytics.router, prefix="/api/drugref")

# ── Email MVP routes ───────────────────────────────────────────────
from apps.email_app.api.routes import members as email_members
from apps.email_app.api.routes import emails as email_emails
from apps.email_app.api.routes import analytics as email_analytics

app.include_router(email_members.router, prefix="/api/email")
app.include_router(email_emails.router, prefix="/api/email")
app.include_router(email_analytics.router, prefix="/api/email")

# ── Acquisition Funnels routes ────────────────────────────────────
from apps.acquisition.api.routes import salary as acq_salary
from apps.acquisition.api.routes import interactions as acq_interactions
from apps.acquisition.api.routes import career as acq_career
from apps.acquisition.api.routes import leads as acq_leads
from apps.acquisition.api.routes import analytics as acq_analytics

app.include_router(acq_salary.router, prefix="/api/acquisition")
app.include_router(acq_interactions.router, prefix="/api/acquisition")
app.include_router(acq_career.router, prefix="/api/acquisition")
app.include_router(acq_leads.router, prefix="/api/acquisition")
app.include_router(acq_analytics.router, prefix="/api/acquisition")

# ── Outreach Automation routes ────────────────────────────────────
from apps.outreach.api.routes import auth as outreach_auth
from apps.outreach.api.routes import prospects as outreach_prospects
from apps.outreach.api.routes import campaigns as outreach_campaigns
from apps.outreach.api.routes import webhooks as outreach_webhooks
from apps.outreach.api.routes import analytics as outreach_analytics

app.include_router(outreach_auth.router, prefix="/api/outreach")
app.include_router(outreach_prospects.router, prefix="/api/outreach")
app.include_router(outreach_campaigns.router, prefix="/api/outreach")
app.include_router(outreach_webhooks.router, prefix="/api/outreach")
app.include_router(outreach_analytics.router, prefix="/api/outreach")


# ── SEO endpoint from CPE ──────────────────────────────────────────
import json
from pathlib import Path


@app.get("/seo/state/{state_code}")
def state_seo(state_code: str):
    data_path = Path(__file__).parent / "apps" / "cpe" / "data" / "state_requirements.json"
    data = json.loads(data_path.read_text())
    state = data.get(state_code.upper(), {})
    if not state:
        return {"error": "State not found"}
    return {
        "title": f"{state['name']} Pharmacist CPE Requirements 2026 | Free Gap Calculator",
        "description": (
            f"Free tool: calculate your {state['name']} pharmacist CPE gap. "
            f"{state['name']} requires {state['hours_required']} hours every "
            f"{state['cycle_years']} year(s). Get your personalized plan in 30 seconds."
        ),
        "hours_required": state["hours_required"],
        "state_name": state["name"],
    }


# ── Startup ────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("Creating all DB tables...")

    # Import all models so they register with Base.metadata
    import apps.churn.db.models.member  # noqa: F401
    import apps.churn.db.models.churn_score  # noqa: F401
    import apps.churn.db.models.alert  # noqa: F401
    import apps.concierge.db.models.conversation  # noqa: F401
    import apps.concierge.db.models.lead  # noqa: F401
    import apps.cpe.db.models.calculation  # noqa: F401
    import apps.cpe.db.models.lead  # noqa: F401
    import apps.crosssell.db.models.member  # noqa: F401
    import apps.crosssell.db.models.crosssell_score  # noqa: F401
    import apps.crosssell.db.models.nudge  # noqa: F401
    import apps.crosssell.db.models.conversion  # noqa: F401
    import apps.drug_ref.db.models.user  # noqa: F401
    import apps.drug_ref.db.models.subscription  # noqa: F401
    import apps.drug_ref.db.models.api_key  # noqa: F401
    import apps.drug_ref.db.models.organization  # noqa: F401
    import apps.drug_ref.db.models.query_log  # noqa: F401
    import apps.drug_ref.db.models.content_source  # noqa: F401
    import apps.email_app.db.models.member  # noqa: F401
    import apps.email_app.db.models.email_send  # noqa: F401
    import apps.email_app.db.models.email_event  # noqa: F401
    import apps.acquisition.db.models.usage  # noqa: F401
    import apps.acquisition.db.models.lead  # noqa: F401
    import apps.outreach.db.models.prospect  # noqa: F401
    import apps.outreach.db.models.campaign  # noqa: F401
    import apps.outreach.db.models.email_sequence  # noqa: F401
    import apps.outreach.db.models.email_send  # noqa: F401
    import apps.outreach.db.models.suppression  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("All tables created.")

    # Seed churn members
    from apps.churn.db.models.member import Member as ChurnMember
    db = SessionLocal()
    try:
        if db.query(ChurnMember).count() == 0:
            logger.info("Seeding churn mock members...")
            from apps.churn.utils.seed_data import generate_mock_members
            for m in generate_mock_members(200):
                db.add(ChurnMember(**m))
            db.commit()
            logger.info("Churn: seeded 200 members.")
    finally:
        db.close()

    # Seed crosssell members
    from apps.crosssell.db.models.member import Member as CrossSellMember
    db = SessionLocal()
    try:
        if db.query(CrossSellMember).count() == 0:
            logger.info("Seeding crosssell mock members...")
            from apps.crosssell.utils.seed_data import generate_mock_members as crosssell_seed
            for m in crosssell_seed(150):
                db.add(CrossSellMember(**m))
            db.commit()
            logger.info("CrossSell: seeded 150 members.")
    finally:
        db.close()

    # Seed email members
    from apps.email_app.utils.seed_data import seed_members
    db = SessionLocal()
    try:
        seed_members(db, count=200)
        logger.info("Email: seeded 200 members.")
    finally:
        db.close()

    # Seed outreach prospects
    from apps.outreach.db.models.prospect import Prospect as OutreachProspect
    db = SessionLocal()
    try:
        if db.query(OutreachProspect).count() == 0:
            logger.info("Seeding outreach mock prospects...")
            from apps.outreach.pipeline.npi_importer import run_npi_import
            run_npi_import(db, use_mock=True, max_per_state=100)
            logger.info("Outreach: seeded prospects.")
    finally:
        db.close()

    # Init concierge vector store
    try:
        from apps.concierge.rag.retriever import get_vector_store
        get_vector_store()
        logger.info("Concierge vector store initialized.")
    except Exception as e:
        logger.warning(f"Concierge vector store init skipped: {e}")

    # Ingest drug reference clinical content into ChromaDB
    try:
        from apps.drug_ref.rag.vector_store import get_vector_store as get_drugref_store
        drugref_store = get_drugref_store()
        if drugref_store.count() == 0:
            logger.info("Drug Reference: ingesting clinical content...")
            from apps.drug_ref.rag.ingestion.pipeline import IngestionPipeline
            pipeline = IngestionPipeline()
            results = pipeline.run()
            total_chunks = sum(r["chunk_count"] for r in results)
            logger.info(f"Drug Reference: ingested {len(results)} documents, {total_chunks} chunks.")
        else:
            logger.info(f"Drug Reference: {drugref_store.count()} chunks already in store.")
    except Exception as e:
        logger.warning(f"Drug Reference ingestion skipped: {e}")

    logger.info("Master API startup complete.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-master-api"}


@app.get("/")
def root():
    return {
        "service": "APhA AI Master API",
        "status": "ok",
        "version": "1.0.0",
        "mvps": {
            "churn": "/api/churn",
            "concierge": "/api/concierge",
            "cpe": "/api/cpe",
            "crosssell": "/api/crosssell",
            "drugref": "/api/drugref",
            "email": "/api/email",
            "acquisition": "/api/acquisition",
            "outreach": "/api/outreach",
        },
        "docs": "/docs",
    }
