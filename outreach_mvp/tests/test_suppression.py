import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ["DATABASE_URL"] = "sqlite:///./test_outreach.db"
os.environ["REDIS_URL"] = "redis://localhost:6383/0"
os.environ["ENV"] = "development"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from db.models.suppression import Suppression
from delivery.suppression_manager import is_suppressed, add_suppression


def _get_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_suppression_add_and_check():
    db = _get_db()
    assert is_suppressed("test@pharmacy.com", db) is False
    add_suppression("test@pharmacy.com", "unsubscribe", db)
    assert is_suppressed("test@pharmacy.com", db) is True
    assert is_suppressed("TEST@PHARMACY.COM", db) is True


def test_suppression_idempotent():
    db = _get_db()
    add_suppression("dup@test.com", "unsubscribe", db)
    add_suppression("dup@test.com", "unsubscribe", db)
    count = db.query(Suppression).filter(Suppression.email == "dup@test.com").count()
    assert count == 1
