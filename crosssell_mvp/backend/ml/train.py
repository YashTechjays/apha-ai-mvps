import mlflow
import mlflow.xgboost
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score
from backend.ml.features import FEATURE_NAMES, PRODUCTS
from backend.utils.seed_data import generate_training_dataset
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def train_product_model(product: str):
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(f"apha_crosssell_{product}")

    logger.info(f"Generating training data for product: {product}")
    df = generate_training_dataset(product=product, n_samples=3000)
    X = df[FEATURE_NAMES]
    y = df["will_engage"]
    logger.info(f"{product}: {len(df)} samples, {y.mean():.1%} engagement rate")

    params = {
        "n_estimators": 200, "max_depth": 4, "learning_rate": 0.08,
        "subsample": 0.8, "colsample_bytree": 0.8,
        "scale_pos_weight": (y == 0).sum() / max((y == 1).sum(), 1),
        "eval_metric": "auc", "random_state": 42,
    }

    with mlflow.start_run(run_name=f"{product}_model"):
        mlflow.log_params({"product": product, **params})
        model = XGBClassifier(**params)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
        logger.info(f"{product} CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        mlflow.log_metric("cv_auc_mean", cv_scores.mean())
        model.fit(X, y)
        train_auc = roc_auc_score(y, model.predict_proba(X)[:, 1])
        mlflow.log_metric("train_auc", train_auc)
        try:
            mlflow.xgboost.log_model(
                model, f"crosssell_{product}_model",
                registered_model_name=f"apha_crosssell_{product}"
            )
        except Exception as e:
            logger.warning(f"MLflow registry not available, model in-memory only: {e}")
        logger.info(f"{product} model trained. AUC: {train_auc:.4f}")
    return model


def train_all_models():
    models = {}
    for product in PRODUCTS:
        models[product] = train_product_model(product)
    return models


if __name__ == "__main__":
    train_all_models()
