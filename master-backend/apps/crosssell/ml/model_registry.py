import mlflow
import mlflow.xgboost
from apps.crosssell.utils.config import get_settings
from apps.crosssell.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_models_cache = {}


def load_models() -> dict:
    global _models_cache
    if _models_cache:
        return _models_cache

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    models = {}
    for product in settings.products:
        try:
            client = mlflow.MlflowClient()
            versions = client.get_latest_versions(
                f"apha_crosssell_{product}", stages=["None", "Production"]
            )
            if versions:
                uri = f"models:/apha_crosssell_{product}/{versions[-1].version}"
                models[product] = mlflow.xgboost.load_model(uri)
                logger.info(f"Loaded model: {product} v{versions[-1].version}")
        except Exception as e:
            logger.warning(f"Could not load model for {product}: {e}. Training fallback.")

    if not models:
        from apps.crosssell.ml.train import train_all_models
        models = train_all_models()

    _models_cache = models
    return models
