"""Load the latest trained model from MLflow."""
import mlflow
import mlflow.xgboost
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_model_cache = None
_model_version_cache = None


def load_latest_model():
    global _model_cache, _model_version_cache

    if _model_cache is not None:
        return _model_cache, _model_version_cache

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    try:
        client = mlflow.MlflowClient()
        versions = client.get_latest_versions("apha_churn_v1", stages=["None", "Production"])
        if versions:
            latest = versions[-1]
            model_uri = f"models:/apha_churn_v1/{latest.version}"
            model = mlflow.xgboost.load_model(model_uri)
            _model_cache = model
            _model_version_cache = f"v{latest.version}"
            logger.info(f"Loaded model version {_model_version_cache}")
            return model, _model_version_cache
    except Exception as e:
        logger.warning(f"Could not load from MLflow registry: {e}. Training fallback model.")

    from backend.ml.train import train_model
    model = train_model()
    _model_cache = model
    _model_version_cache = "v1-fallback"
    return model, _model_version_cache
