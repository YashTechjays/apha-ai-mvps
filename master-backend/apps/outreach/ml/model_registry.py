"""Load ICP model from MLflow registry with fallback training."""
import mlflow
import mlflow.xgboost
from apps.outreach.utils.config import get_settings
from apps.outreach.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
_model_cache = None


def load_icp_model():
    global _model_cache
    if _model_cache:
        return _model_cache

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    try:
        client = mlflow.MlflowClient()
        versions = client.get_latest_versions("apha_icp_v1", stages=["None", "Production"])
        if versions:
            uri = f"models:/apha_icp_v1/{versions[-1].version}"
            _model_cache = mlflow.xgboost.load_model(uri)
            logger.info(f"Loaded ICP model v{versions[-1].version}")
            return _model_cache
    except Exception as e:
        logger.warning(f"MLflow load failed: {e}. Training fallback.")

    from ml.icp_train import train_icp_model
    _model_cache = train_icp_model()
    return _model_cache
