"""
Suppression list management -- CAN-SPAM compliance.
Always check before any send. Honor unsubscribes immediately.
"""
from sqlalchemy.orm import Session
from db.models.suppression import Suppression
from db.models.prospect import Prospect
from utils.logger import get_logger

logger = get_logger(__name__)


def is_suppressed(email: str, db: Session) -> bool:
    return db.query(Suppression).filter(
        Suppression.email == email.lower().strip()
    ).first() is not None


def add_suppression(email: str, reason: str, db: Session, source: str = "webhook"):
    """Add email to suppression list. Idempotent."""
    email = email.lower().strip()
    existing = db.query(Suppression).filter(Suppression.email == email).first()
    if existing:
        return

    db.add(Suppression(email=email, reason=reason, source=source))

    prospect = db.query(Prospect).filter(Prospect.email == email).first()
    if prospect:
        if reason == "unsubscribe":
            prospect.status = "unsubscribed"
        elif reason == "hard_bounce":
            prospect.status = "bounced"
        prospect.do_not_contact = True

    db.commit()
    logger.info(f"Suppressed: {email} | reason={reason}")


def bulk_check(emails: list, db: Session) -> set:
    """Return set of suppressed emails from a list."""
    suppressed = db.query(Suppression.email).filter(
        Suppression.email.in_([e.lower() for e in emails])
    ).all()
    return {s.email for s in suppressed}
