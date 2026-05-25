"""
Feature engineering for the ICP (Ideal Customer Profile) scoring model.

The ICP model answers: "How likely is this non-member pharmacist to convert
if we reach out to them?"

Features are derived from:
  - Professional profile (license type, specialty, career stage, credentials)
  - Geographic signals (state, market penetration)
  - Practice setting (hospital > community > other for APhA conversion)
  - Inferred career signals (graduation year, years of experience)
  - Email quality signals (verified email = higher reach probability)
"""
import pandas as pd
from apps.outreach.db.models.prospect import Prospect

FEATURE_NAMES = [
    "license_type_encoded",
    "career_stage_encoded",
    "has_pharm_d",
    "has_board_cert",
    "setting_hospital",
    "setting_community",
    "setting_ambulatory",
    "setting_academia",
    "setting_other",
    "state_market_maturity",
    "high_growth_state",
    "years_in_practice",
    "is_new_grad",
    "is_mid_career",
    "is_senior",
    "email_available",
    "email_verified",
    "full_name_quality",
]

SETTING_ENCODING = {
    "hospital/health-system": ("setting_hospital", 0.85),
    "ambulatory care": ("setting_ambulatory", 0.75),
    "academia": ("setting_academia", 0.80),
    "long-term care": ("setting_other", 0.60),
    "community pharmacy": ("setting_community", 0.65),
    "specialty/mail order": ("setting_other", 0.55),
    "general pharmacy": ("setting_other", 0.50),
}

LICENSE_ENCODING = {
    "pharmacist": 3.0,
    "new_practitioner": 2.0,
    "student": 1.0,
    "technician": 0.0,
}

CAREER_ENCODING = {
    "senior": 4.0,
    "mid_career": 3.0,
    "new_practitioner": 2.0,
    "student": 1.0,
    "unknown": 0.0,
}

HIGH_PENETRATION_STATES = {
    "CA", "TX", "NY", "FL", "IL", "PA", "OH", "MA", "NC", "WA"
}

STATE_MATURITY = {
    "CA": 0.8, "TX": 0.75, "NY": 0.78, "FL": 0.72, "IL": 0.70,
    "PA": 0.68, "OH": 0.65, "MA": 0.82, "NC": 0.62, "WA": 0.74,
    "GA": 0.60, "MI": 0.62, "VA": 0.65, "AZ": 0.58, "CO": 0.63,
}


def extract_features(prospect: Prospect) -> dict:
    """Extract ICP features from a single Prospect record."""
    credential = (prospect.credential or "").upper()
    license_type = (prospect.license_type or "pharmacist").lower()
    career_stage = (prospect.career_stage or "unknown").lower()
    setting = (prospect.practice_setting or "general pharmacy").lower()
    state = (prospect.state or "").upper()

    license_enc = LICENSE_ENCODING.get(license_type, 3.0)
    career_enc = CAREER_ENCODING.get(career_stage, 0.0)

    has_pharmd = 1.0 if "PHARMD" in credential or "PHARM.D" in credential else 0.0
    has_board = 1.0 if any(c in credential for c in ["BCPS", "BCACP", "BCOP", "BCPPS", "BCCCP"]) else 0.0

    setting_flags = {
        "setting_hospital": 0.0, "setting_community": 0.0,
        "setting_ambulatory": 0.0, "setting_academia": 0.0, "setting_other": 0.0
    }
    matched_setting = next(
        (v for k, v in SETTING_ENCODING.items() if k in setting),
        ("setting_other", 0.50)
    )
    setting_flags[matched_setting[0]] = 1.0

    state_maturity = STATE_MATURITY.get(state, 0.55)
    high_growth = 1.0 if state in HIGH_PENETRATION_STATES else 0.0

    years = float(prospect.years_since_grad or 5)
    is_new_grad = 1.0 if years <= 2 else 0.0
    is_mid = 1.0 if 3 <= years <= 10 else 0.0
    is_senior = 1.0 if years > 10 else 0.0

    email_avail = 1.0 if prospect.email else 0.0
    email_verified = 1.0 if prospect.email_verified else 0.0
    name_quality = 1.0 if (prospect.first_name and prospect.last_name
                            and len(prospect.first_name) > 1
                            and len(prospect.last_name) > 1) else 0.0

    return {
        "license_type_encoded": license_enc,
        "career_stage_encoded": career_enc,
        "has_pharm_d": has_pharmd,
        "has_board_cert": has_board,
        **setting_flags,
        "state_market_maturity": state_maturity,
        "high_growth_state": high_growth,
        "years_in_practice": min(years / 30, 1.0),
        "is_new_grad": is_new_grad,
        "is_mid_career": is_mid,
        "is_senior": is_senior,
        "email_available": email_avail,
        "email_verified": email_verified,
        "full_name_quality": name_quality,
    }


def prospects_to_dataframe(prospects: list) -> pd.DataFrame:
    rows = [extract_features(p) for p in prospects]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)
