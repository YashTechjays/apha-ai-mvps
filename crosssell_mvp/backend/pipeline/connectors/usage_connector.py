import random
from sqlalchemy.orm import Session
from backend.db.models.member import Member
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def pull_all_product_usage(db: Session):
    """Update all 5 product stream usage fields for all members."""
    members = db.query(Member).filter(Member.is_active == True).all()
    for member in members:
        tier = member.tier if isinstance(member.tier, str) else "pharmacist"

        if random.random() < (0.7 if tier in ("pharmacist", "student") else 0.4):
            member.edu_cpe_hours_ytd = round(random.uniform(2, 20), 1)
            member.edu_courses_completed = random.randint(1, 8)
            member.edu_last_activity_days = random.uniform(1, 60)
            member.edu_active = member.edu_last_activity_days < 90
        else:
            member.edu_active = False
            member.edu_last_activity_days = random.uniform(90, 365)

        if random.random() < (0.6 if tier in ("researcher", "pharmacist") else 0.3):
            member.pub_articles_read_30d = random.randint(1, 15)
            member.pub_pharmacylibrary_sessions = random.randint(0, 10)
            member.pub_last_activity_days = random.uniform(1, 45)
            member.pub_active = True
        else:
            member.pub_active = False
            member.pub_last_activity_days = random.uniform(90, 400)

        if random.random() < 0.35:
            member.events_attended_ytd = random.randint(1, 5)
            member.events_last_attended_days = random.uniform(1, 120)
            member.events_active = True
        else:
            member.events_active = False
            member.events_last_attended_days = random.uniform(120, 500)

        if random.random() < (0.5 if tier in ("new_practitioner", "student") else 0.2):
            member.career_job_searches = random.randint(1, 20)
            member.career_profile_complete_pct = random.uniform(40, 100)
            member.career_advance_logins = random.randint(1, 10)
            member.career_active = True
        else:
            member.career_active = False

        if random.random() < (0.3 if (member.years_as_member or 0) > 3 else 0.1):
            member.advocacy_action_center_visits = random.randint(1, 6)
            member.advocacy_letters_sent = random.randint(0, 5)
            member.advocacy_active = True
        else:
            member.advocacy_active = False

        member.active_stream_count = sum([
            bool(member.edu_active), bool(member.pub_active),
            bool(member.events_active), bool(member.career_active),
            bool(member.advocacy_active),
        ])

    db.commit()
    logger.info(f"Usage sync: updated {len(members)} members across all 5 product streams")
