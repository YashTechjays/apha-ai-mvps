import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from backend.db.models.member import Member, MemberTier

fake = Faker()
TIERS = [MemberTier.PHARMACIST, MemberTier.STUDENT, MemberTier.TECHNICIAN, MemberTier.ASSOCIATE]
TIER_WEIGHTS = [0.65, 0.15, 0.12, 0.08]


def _random_member() -> Member:
    tier = random.choices(TIERS, weights=TIER_WEIGHTS)[0]
    join_date = fake.date_time_between(start_date="-5y", end_date="-30d")
    days_ago = random.randint(0, 90)
    return Member(
        id=str(uuid.uuid4()),
        email=fake.unique.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        tier=tier,
        join_date=join_date,
        renewal_date=join_date + timedelta(days=365),
        is_active=True,
        cpe_credits_ytd=round(random.uniform(0, 30), 1),
        cpe_courses_completed=random.randint(0, 12),
        webinars_attended_ytd=random.randint(0, 8),
        journal_articles_read_ytd=random.randint(0, 40),
        pharmacylibrary_sessions_ytd=random.randint(0, 50),
        annual_meeting_attended=random.random() < 0.20,
        events_registered_ytd=random.randint(0, 5),
        last_login_date=datetime.utcnow() - timedelta(days=days_ago),
        days_since_last_login=days_ago,
        email_open_rate=round(random.uniform(0.05, 0.80), 2),
        portal_sessions_last_30d=random.randint(0, 25),
        career_center_applications=random.randint(0, 4),
        advocacy_actions_ytd=random.randint(0, 6),
    )


def seed_members(db: Session, count: int = 200) -> None:
    existing = db.query(Member).count()
    if existing >= count:
        return
    needed = count - existing
    for _ in range(needed):
        db.add(_random_member())
    db.commit()
