"""
Train the churn prediction model on historical member data.
In production: called by the Airflow DAG monthly.
For MVP: run manually with `python -m backend.ml.train`
"""
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score
import mlflow
import mlflow.xgboost
from apps.churn.utils.config import get_settings
from apps.churn.utils.logger import get_logger
from apps.churn.ml.features import FEATURE_NAMES
from apps.churn.utils.seed_data import generate_training_dataset

logger = get_logger(__name__)
settings = get_settings()


def train_model():
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("apha_churn_prediction")

    logger.info("Generating training dataset...")
    df = generate_training_dataset(n_samples=5000)
    X = df[FEATURE_NAMES]
    y = df["churned"]
    logger.info(f"Dataset: {len(df)} samples, {y.mean():.1%} churn rate")

    params = {
        "n_estimators": 300,
        "max_depth": 5,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": (y == 0).sum() / (y == 1).sum(),
        "eval_metric": "auc",
        "random_state": 42,
    }

    with mlflow.start_run():
        mlflow.log_params(params)
        model = XGBClassifier(**params)

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
        logger.info(f"CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        mlflow.log_metric("cv_auc_mean", float(cv_scores.mean()))
        mlflow.log_metric("cv_auc_std", float(cv_scores.std()))

        model.fit(X, y)
        train_preds = model.predict_proba(X)[:, 1]
        train_auc = roc_auc_score(y, train_preds)
        mlflow.log_metric("train_auc", train_auc)

        mlflow.xgboost.log_model(model, "churn_model", registered_model_name="apha_churn_v1")
        logger.info(f"Model trained. Train AUC: {train_auc:.4f}")

        importances = sorted(
            zip(FEATURE_NAMES, model.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        logger.info("Feature importances (top 5):")
        for feat, imp in importances:
            logger.info(f"  {feat}: {imp:.4f}")

    return model


if __name__ == "__main__":
    train_model()
