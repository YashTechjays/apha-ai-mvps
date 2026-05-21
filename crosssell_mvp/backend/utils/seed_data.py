import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

TIERS = ["student", "new_practitioner", "pharmacist", "technician", "researcher"]
SPECIALTIES = [
    "Hospital/Health-System", "Community Pharmacy", "Ambulatory Care",
    "Long-Term Care", "Managed Care", "Academia", "Industry",
]
STATES = ["CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI"]


def generate_mock_members(n: int = 150) -> list:
    members = []
    for _ in range(n):
        tier = random.choice(TIERS)
        years = random.uniform(0.5, 12)
        join_dt = datetime.now() - timedelta(days=int(years * 365))
        renewal_dt = datetime.now() + timedelta(days=random.randint(30, 365))

        active_streams = random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.35, 0.2, 0.1, 0.05])[0]
        stream_pool = ["edu", "pub", "events", "career", "advocacy"]
        active_set = set(random.sample(stream_pool, min(active_streams, len(stream_pool))))

        edu_active = "edu" in active_set
        pub_active = "pub" in active_set
        events_active = "events" in active_set
        career_active = "career" in active_set
        advocacy_active = "advocacy" in active_set

        members.append({
            "external_id": f"CRM-{fake.unique.random_int(10000, 99999)}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "tier": tier,
            "state": random.choice(STATES),
            "specialty": random.choice(SPECIALTIES),
            "join_date": join_dt,
            "renewal_date": renewal_dt,
            "is_active": True,
            "years_as_member": round(years, 1),
            "renewal_count": random.randint(0, int(years) + 1),
            "churn_score": round(random.uniform(10, 85), 1),
            "edu_cpe_hours_ytd": round(random.uniform(2, 18), 1) if edu_active else 0,
            "edu_courses_completed": random.randint(1, 6) if edu_active else 0,
            "edu_last_activity_days": random.uniform(5, 60) if edu_active else random.uniform(90, 400),
            "edu_certificates_earned": random.randint(0, 3) if edu_active else 0,
            "edu_active": edu_active,
            "pub_articles_read_30d": random.randint(1, 12) if pub_active else 0,
            "pub_pharmacylibrary_sessions": random.randint(0, 8) if pub_active else 0,
            "pub_journal_downloads": random.randint(0, 5) if pub_active else 0,
            "pub_last_activity_days": random.uniform(5, 45) if pub_active else random.uniform(90, 400),
            "pub_active": pub_active,
            "events_attended_ytd": random.randint(1, 4) if events_active else 0,
            "events_registered_ytd": random.randint(1, 5) if events_active else 0,
            "events_last_attended_days": random.uniform(5, 120) if events_active else random.uniform(120, 500),
            "events_annual_meeting_attended": random.random() < 0.3 if events_active else False,
            "events_active": events_active,
            "career_job_searches": random.randint(1, 15) if career_active else 0,
            "career_profile_complete_pct": random.uniform(50, 100) if career_active else random.uniform(0, 30),
            "career_applications": random.randint(0, 5) if career_active else 0,
            "career_advance_logins": random.randint(1, 8) if career_active else 0,
            "career_active": career_active,
            "advocacy_action_center_visits": random.randint(1, 6) if advocacy_active else 0,
            "advocacy_letters_sent": random.randint(0, 4) if advocacy_active else 0,
            "advocacy_pac_donor": random.random() < 0.2 if advocacy_active else False,
            "advocacy_newsletter_opens": random.randint(0, 10) if advocacy_active else 0,
            "advocacy_active": advocacy_active,
            "active_stream_count": len(active_set),
        })
    return members


def generate_training_dataset(product: str, n_samples: int = 3000):
    import pandas as pd

    rows = []
    for _ in range(n_samples):
        tier = random.choice(TIERS)
        tier_enc = {
            "student": 0, "new_practitioner": 1, "technician": 2,
            "supporter": 3, "pharmacist": 4, "researcher": 5,
        }.get(tier, 4)
        overall_engagement = random.uniform(0, 1)
        product_usage = random.uniform(0, 0.5)
        churn = random.uniform(0.1, 0.8)
        tenure = random.uniform(0.5, 10)
        other_active = random.randint(1, 4)

        prob = (
            overall_engagement * 0.4 +
            (1 - product_usage) * 0.3 +
            (1 - churn) * 0.2 +
            min(tenure / 5, 1) * 0.1
        )
        will_engage = int(random.random() < prob)

        rows.append({
            "tenure_years": tenure,
            "renewal_count": int(tenure * 0.8),
            "tier_encoded": float(tier_enc),
            "churn_score_normalized": churn,
            "active_stream_count": float(other_active),
            "product_usage_score": product_usage,
            "product_last_activity_days_norm": random.uniform(0.3, 1),
            "product_already_active": 0.0,
            "other_streams_active_count": float(other_active),
            "edu_active_flag": float(random.random() < 0.5),
            "pub_active_flag": float(random.random() < 0.4),
            "events_active_flag": float(random.random() < 0.35),
            "career_active_flag": float(random.random() < 0.3),
            "advocacy_active_flag": float(random.random() < 0.2),
            "overall_engagement_score": overall_engagement,
            "email_open_rate": random.uniform(0.1, 0.6),
            "login_recency_score": random.uniform(0.2, 1),
            "is_student": float(tier == "student"),
            "is_researcher": float(tier == "researcher"),
            "is_hospital_pharmacist": float(random.random() < 0.2),
            "times_nudged_this_product": float(random.randint(0, 2)),
            "days_since_last_nudge": random.uniform(0, 1),
            "will_engage": will_engage,
        })
    return pd.DataFrame(rows)
