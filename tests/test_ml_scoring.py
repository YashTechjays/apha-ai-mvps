from backend.utils.seed_data import generate_training_dataset
from backend.ml.features import FEATURE_NAMES
from backend.ml.train import train_model


def test_training_dataset_shape():
    df = generate_training_dataset(200)
    assert len(df) == 200
    for col in FEATURE_NAMES:
        assert col in df.columns


def test_model_trains_and_predicts():
    model = train_model()
    df = generate_training_dataset(50)
    X = df[FEATURE_NAMES]
    preds = model.predict_proba(X)[:, 1]
    assert len(preds) == 50
    assert all(0 <= p <= 1 for p in preds)
