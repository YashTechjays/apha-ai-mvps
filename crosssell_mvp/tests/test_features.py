from backend.db.models.member import Member
from backend.ml.features import extract_features, FEATURE_NAMES, PRODUCTS


def _make_member(**kwargs):
    m = Member()
    defaults = {
        "tier": "pharmacist", "years_as_member": 3, "renewal_count": 2,
        "churn_score": 40, "active_stream_count": 2,
        "edu_active": True, "pub_active": False, "events_active": False,
        "career_active": False, "advocacy_active": False,
        "edu_cpe_hours_ytd": 10, "edu_courses_completed": 3,
        "edu_last_activity_days": 15,
        "pub_articles_read_30d": 0, "pub_pharmacylibrary_sessions": 0, "pub_last_activity_days": 200,
        "events_attended_ytd": 0, "events_last_attended_days": 300, "events_annual_meeting_attended": False,
        "career_job_searches": 0, "career_profile_complete_pct": 0,
        "advocacy_action_center_visits": 0, "advocacy_letters_sent": 0,
        "specialty": "Community Pharmacy",
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


def test_feature_count():
    assert len(FEATURE_NAMES) == 22


def test_extract_features_all_keys():
    m = _make_member()
    for product in PRODUCTS:
        features = extract_features(m, product)
        for name in FEATURE_NAMES:
            assert name in features, f"Missing feature: {name} for product: {product}"


def test_already_active_product_marked():
    m = _make_member(edu_active=True, edu_cpe_hours_ytd=15)
    f = extract_features(m, "education")
    assert f["product_already_active"] == 1.0


def test_inactive_product_marked_zero():
    m = _make_member(pub_active=False, pub_articles_read_30d=0)
    f = extract_features(m, "publications")
    assert f["product_already_active"] == 0.0


def test_other_streams_count_excludes_target():
    m = _make_member(edu_active=True, pub_active=True, events_active=True)
    f = extract_features(m, "education")
    # other streams active: pub + events = 2
    assert f["other_streams_active_count"] == 2.0
