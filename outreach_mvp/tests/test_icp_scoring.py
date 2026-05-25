import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ["DATABASE_URL"] = "sqlite:///./test_outreach.db"
os.environ["REDIS_URL"] = "redis://localhost:6383/0"
os.environ["ENV"] = "development"

from db.models.prospect import Prospect
from ml.icp_features import extract_features, FEATURE_NAMES, prospects_to_dataframe


def _make_prospect(**kwargs):
    p = Prospect()
    defaults = {
        "first_name": "Jane", "last_name": "Doe",
        "email": "jane@hospital.com", "credential": "PharmD",
        "license_type": "pharmacist", "specialty": "Hospital/Health-System",
        "practice_setting": "Hospital/Health-System", "state": "TX",
        "career_stage": "mid_career", "years_since_grad": 7,
        "email_verified": True,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(p, k, v)
    return p


def test_feature_count():
    assert len(FEATURE_NAMES) == 18


def test_extract_features_all_keys():
    p = _make_prospect()
    features = extract_features(p)
    for name in FEATURE_NAMES:
        assert name in features, f"Missing feature: {name}"


def test_hospital_pharmacist_higher_setting_score():
    hospital = _make_prospect(practice_setting="Hospital/Health-System")
    community = _make_prospect(practice_setting="Community Pharmacy")
    h_feat = extract_features(hospital)
    c_feat = extract_features(community)
    assert h_feat["setting_hospital"] == 1.0
    assert c_feat["setting_community"] == 1.0


def test_prospects_to_dataframe():
    prospects = [_make_prospect() for _ in range(5)]
    df = prospects_to_dataframe(prospects)
    assert len(df) == 5
    assert list(df.columns) == FEATURE_NAMES
