import os
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from fastapi.testclient import TestClient

# Patch PG UUID to be sqlite-compatible BEFORE importing models
_orig_impl = PG_UUID.load_dialect_impl
_orig_bind = PG_UUID.process_bind_param if hasattr(PG_UUID, "process_bind_param") else None


def _patched_impl(self, dialect):
    if dialect.name == "sqlite":
        return dialect.type_descriptor(CHAR(36))
    return _orig_impl(self, dialect)


def _patched_bind(self, value, dialect):
    if value is None:
        return None
    if dialect.name == "sqlite":
        return str(value) if isinstance(value, uuid.UUID) else value
    if _orig_bind:
        return _orig_bind(self, value, dialect)
    return value


PG_UUID.load_dialect_impl = _patched_impl
PG_UUID.process_bind_param = _patched_bind

from backend.db.base import Base
from backend.db.session import get_db
from backend.db.models import Calculation, Lead  # noqa
from backend.main import app

engine = create_engine("sqlite:///./test_cpe.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def _no_anthropic(monkeypatch):
    # Force fallback plan path so tests don't hit Claude API
    from backend.ai import planner
    monkeypatch.setattr(planner, "client", None)
