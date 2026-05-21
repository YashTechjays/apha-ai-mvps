"""FastAPI entrypoint for APhA Clinical Assistant."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import analytics, auth, query, subscriptions, webhooks
from backend.db.base import Base
from backend.db.session import engine
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="APhA Clinical Assistant API",
    description="B2B clinical drug reference and decision-support API powered by APhA content + Claude.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3005", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Best-effort table creation for local dev; production uses Alembic migrations
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Table create_all skipped: {e}")
    logger.info("APhA Clinical Assistant API started.")


@app.get("/", tags=["meta"])
def root():
    return {
        "service": "APhA Clinical Assistant",
        "status": "ok",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
