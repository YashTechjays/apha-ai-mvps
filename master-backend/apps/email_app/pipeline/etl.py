from datetime import datetime
from sqlalchemy.orm import Session
from apps.email_app.db.models.member import Member
from apps.email_app.pipeline.connectors import (
    lms_connector, crm_connector, events_connector, publications_connector
)
from apps.email_app.utils.logger import get_logger

logger = get_logger(__name__)


def sync_member_activity(db: Session, member: Member) -> None:
    lms = lms_connector.fetch_cpe_activity(member)
    member.cpe_credits_ytd = round(member.cpe_credits_ytd + lms["cpe_credits_delta"], 1)
    member.cpe_courses_completed += lms["courses_delta"]
    member.webinars_attended_ytd += lms["webinars_delta"]

    crm = crm_connector.fetch_portal_activity(member)
    member.last_login_date = crm["last_login_date"]
    member.days_since_last_login = crm["days_since_last_login"]
    member.portal_sessions_last_30d = crm["portal_sessions_last_30d"]
    member.email_open_rate = crm["email_open_rate"]
    member.career_center_applications = crm["career_center_applications"]
    member.advocacy_actions_ytd = crm["advocacy_actions_ytd"]

    events = events_connector.fetch_events_activity(member)
    member.annual_meeting_attended = events["annual_meeting_attended"]
    member.events_registered_ytd = events["events_registered_ytd"]

    pubs = publications_connector.fetch_publication_activity(member)
    member.journal_articles_read_ytd = pubs["journal_articles_read_ytd"]
    member.pharmacylibrary_sessions_ytd = pubs["pharmacylibrary_sessions_ytd"]

    member.updated_at = datetime.utcnow()


def run_full_sync(db: Session) -> int:
    members = db.query(Member).filter(Member.is_active == True).all()
    count = 0
    for member in members:
        try:
            sync_member_activity(db, member)
            count += 1
        except Exception as exc:
            logger.error(f"ETL sync failed for member {member.id}: {exc}")
    db.commit()
    logger.info(f"ETL sync complete: {count}/{len(members)} members updated")
    return count
