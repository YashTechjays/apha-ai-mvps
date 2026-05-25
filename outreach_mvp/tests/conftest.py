import sys
import os
import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Override settings before any imports
os.environ["DATABASE_URL"] = "sqlite:///./test_outreach.db"
os.environ["REDIS_URL"] = "redis://localhost:6383/0"
os.environ["ENV"] = "development"
os.environ["ANTHROPIC_API_KEY"] = "test-key"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from db.session import get_db
from main import app

engine = create_engine("sqlite:///./test_outreach.db", connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    r = client.post("/auth/login", data={"username": "admin", "password": "apha2026"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
