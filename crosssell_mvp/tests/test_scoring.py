from backend.utils.seed_data import generate_training_dataset
from backend.ml.features import FEATURE_NAMES


def test_training_dataset_shape():
    df = generate_training_dataset("education", n_samples=200)
    assert len(df) == 200
    for col in FEATURE_NAMES:
        assert col in df.columns
    assert "will_engage" in df.columns


def test_training_dataset_label_balance():
    df = generate_training_dataset("publications", n_samples=500)
    pos_rate = df["will_engage"].mean()
    assert 0.1 < pos_rate < 0.9, f"Engagement rate {pos_rate} unrealistic"
