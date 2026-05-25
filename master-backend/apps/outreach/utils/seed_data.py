"""Mock prospect + ICP training data generators."""
import random
from datetime import datetime
from faker import Faker
import pandas as pd

fake = Faker()
Faker.seed(42)
random.seed(42)

LICENSE_TYPES = ["pharmacist", "new_practitioner", "technician", "student"]
SPECIALTIES = [
    "Hospital/Health-System", "Community Pharmacy", "Ambulatory Care",
    "Long-Term Care", "Academia", "Specialty/Mail Order"
]
CAREER_STAGES = ["student", "new_practitioner", "mid_career", "senior"]
CREDENTIALS = ["PharmD", "RPh", "PharmD, RPh", "PharmD, BCPS", "PharmD, BCACP", "CPhT"]
STATES = ["CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI",
          "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"]


def generate_mock_prospects(n: int = 300) -> list:
    """Generate mock prospect dicts for seeding."""
    prospects = []
    for _ in range(n):
        license_type = random.choice(LICENSE_TYPES)
        career_stage = random.choice(CAREER_STAGES)
        grad_year = datetime.now().year - random.randint(0, 25)

        prospects.append({
            "npi_number": f"NPI-{fake.unique.random_int(1000000000, 9999999999)}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email() if random.random() > 0.2 else None,
            "credential": random.choice(CREDENTIALS),
            "license_type": license_type,
            "specialty": random.choice(SPECIALTIES),
            "practice_setting": random.choice(SPECIALTIES),
            "state": random.choice(STATES),
            "city": fake.city(),
            "zip_code": fake.zipcode()[:5],
            "career_stage": career_stage,
            "graduation_year": grad_year,
            "years_since_grad": datetime.now().year - grad_year,
            "source": "npi_registry",
            "status": "new",
            "email_verified": random.random() > 0.6,
            "do_not_contact": False,
        })
    return prospects


def generate_icp_training_data(n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic ICP training data with realistic conversion patterns."""
    rows = []
    for _ in range(n_samples):
        license_enc = float(random.choice([0, 1, 2, 3]))
        career_enc = float(random.choice([0, 1, 2, 3, 4]))
        has_pharmd = float(random.random() > 0.4)
        has_board = float(random.random() > 0.8)
        setting_h = float(random.random() > 0.7)
        state_mat = random.uniform(0.5, 0.85)
        email_avail = float(random.random() > 0.2)
        years = random.uniform(0, 1)

        prob = (
            (license_enc / 3) * 0.25 +
            (career_enc / 4) * 0.15 +
            has_pharmd * 0.1 +
            has_board * 0.15 +
            setting_h * 0.1 +
            state_mat * 0.1 +
            email_avail * 0.1 +
            (1 - years) * 0.05
        )
        converted = int(random.random() < prob * 0.35)

        rows.append({
            "license_type_encoded": license_enc,
            "career_stage_encoded": career_enc,
            "has_pharm_d": has_pharmd,
            "has_board_cert": has_board,
            "setting_hospital": setting_h,
            "setting_community": float(random.random() > 0.6),
            "setting_ambulatory": float(random.random() > 0.75),
            "setting_academia": float(random.random() > 0.85),
            "setting_other": float(random.random() > 0.5),
            "state_market_maturity": state_mat,
            "high_growth_state": float(random.random() > 0.5),
            "years_in_practice": years,
            "is_new_grad": float(years < 0.1),
            "is_mid_career": float(0.1 <= years <= 0.4),
            "is_senior": float(years > 0.4),
            "email_available": email_avail,
            "email_verified": float(random.random() > 0.5),
            "full_name_quality": float(random.random() > 0.1),
            "converted": converted,
        })

    return pd.DataFrame(rows)
