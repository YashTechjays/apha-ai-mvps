"""
Train the ICP conversion prediction model.
Labels: 1 = converted to APhA member, 0 = did not convert.
"""
import numpy as np
import pandas as pd
import mlflow
import mlflow.xgboost
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score
from ml.icp_features import FEATURE_NAMES
from utils.seed_data import generate_icp_training_data
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def train_icp_model():
    """Train and register the ICP scoring model."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("apha_icp_scoring")

    logger.info("Generating ICP training dataset...")
    df = generate_icp_training_data(n_samples=5000)
    X = df[FEATURE_NAMES]
    y = df["converted"]

    logger.info(f"Training data: {len(df)} samples, {y.mean():.1%} conversion rate")

    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.08,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": (y == 0).sum() / max((y == 1).sum(), 1),
        "eval_metric": "auc",
        "random_state": 42,
    }

    with mlflow.start_run(run_name="icp_model_v1"):
        mlflow.log_params(params)
        model = XGBClassifier(**params)

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_auc = cross_val_score(model, X, y, cv=cv, scoring="roc_auc").mean()
        mlflow.log_metric("cv_auc", cv_auc)
        logger.info(f"CV AUC: {cv_auc:.4f}")

        model.fit(X, y)
        train_auc = roc_auc_score(y, model.predict_proba(X)[:, 1])
        mlflow.log_metric("train_auc", train_auc)

        mlflow.xgboost.log_model(
            model, "icp_model",
            registered_model_name="apha_icp_v1"
        )
        logger.info(f"ICP model trained. AUC: {train_auc:.4f}")

    return model


if __name__ == "__main__":
    train_icp_model()
