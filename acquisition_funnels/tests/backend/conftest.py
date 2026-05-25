import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.base import Base
from backend.db.models import ToolUsage, Lead  # noqa: F401 — register models with Base
from backend.db.session import get_db


# Use SQLite for tests
engine = create_engine(
    "sqlite:///./test_acquisition.db", connect_args={"check_same_thread": False}
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    # Mock the Anthropic client to avoid real API calls
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Test AI response for salary analysis.")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with patch("backend.ai.salary_engine._get_client", return_value=mock_client), \
         patch("backend.ai.interaction_engine._get_client", return_value=mock_client), \
         patch("backend.ai.career_engine._get_client", return_value=mock_client):
        from backend.main import app
        app.dependency_overrides[get_db] = override_get_db
        yield TestClient(app)
        app.dependency_overrides.clear()
