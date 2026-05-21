"""Pytest fixtures — SQLite test DB + LLM disabled."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import CHAR

# Ensure project root importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# SQLAlchemy 2.x's Uuid type (which PG_UUID inherits from) natively supports
# SQLite via CHAR(32) hex storage. No patching needed.
_ = PG_UUID  # keep import for potential future patching


@pytest.fixture(autouse=True)
def disable_llm(monkeypatch):
    """Force the clinical assistant into deterministic fallback mode."""
    from backend.ai import clinical_assistant as ca
    monkeypatch.setattr(ca, "OpenAI", None)
    yield


@pytest.fixture
def test_engine(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}
    )
    from backend.db.base import Base
    from backend.db import models  # noqa: F401 - register models
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_engine, monkeypatch, tmp_path):
    """FastAPI TestClient with SQLite DB and isolated chroma dir."""
    from fastapi.testclient import TestClient
    import backend.db.session as db_session_mod
    from backend.api import deps as deps_mod

    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(db_session_mod, "engine", test_engine)
    monkeypatch.setattr(db_session_mod, "SessionLocal", SessionLocal)
    monkeypatch.setattr(deps_mod, "SessionLocal", SessionLocal)

    # Isolated chroma persist dir
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))

    from backend.main import app
    with TestClient(app) as c:
        yield c
