from backend.utils.seed_data import generate_mock_members
from backend.db.models.member import Member
from backend.ml.features import extract_features, FEATURE_NAMES


def test_feature_names_count():
    assert len(FEATURE_NAMES) == 25


def test_extract_features_returns_all_keys():
    mock = generate_mock_members(1)[0]
    member = Member(**mock)
    features = extract_features(member)
    for name in FEATURE_NAMES:
        assert name in features, f"Missing feature: {name}"


def test_derived_features_in_range():
    mock = generate_mock_members(1)[0]
    member = Member(**mock)
    f = extract_features(member)
    assert 0.0 <= f["engagement_score"] <= 1.0
    assert 0.0 <= f["login_recency_score"] <= 1.0
    assert f["at_risk_behavior_count"] >= 0
