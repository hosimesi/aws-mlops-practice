import os
from pathlib import Path

import requests

from ml.models.models import MODELS
from ml.utils.aws_controller import (
    download_from_s3,
    get_item_from_dynamo_db,
    get_latest_model_path_from_s3,
)
from ml.utils.consts import DYNAMODB_TABLE_NAME, PREPROCESSOR_FILE_NAME, S3_BUCKET_NAME
from ml.utils.logger.logger_config import get_logger
from predictor.schemas.predict_model import PredictModel

logger = get_logger(__name__)


def _get_latest_predictor_models() -> dict[str, PredictModel]:
    ALL_PREDICTOR_MODELS = {}

    for model in [v.value for v in MODELS.__members__.values()]:
        s3_key = get_latest_model_path_from_s3(s3_bucket=S3_BUCKET_NAME, model_name=model.name)

        s3_path = Path(s3_key)
        s3_directory = s3_path.parent
        local_file_path = f"predictor/artifacts/{model.name}"
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path, exist_ok=True)
        download_from_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=str(s3_directory / f"{model.name}.pkl"),
            file_path=os.path.join(local_file_path, "model.pkl"),
        )
        download_from_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=str(s3_directory / PREPROCESSOR_FILE_NAME),
            file_path=os.path.join(str(local_file_path), PREPROCESSOR_FILE_NAME),
        )
        ml_model = model.ml_model()
        ml_model.load(os.path.join(local_file_path, "model.pkl"))
        preprocessor = model.preprocessor()
        preprocessor.load(os.path.join(local_file_path, PREPROCESSOR_FILE_NAME))
        ALL_PREDICTOR_MODELS[model.name] = PredictModel(name=model.name, model=ml_model, preprocessor=preprocessor)
    return ALL_PREDICTOR_MODELS


def get_predictor_models(revision: str | None = None) -> dict[str, PredictModel]:
    ALL_PREDICTOR_MODELS: dict[str, PredictModel] = {}

    if not revision:
        return _get_latest_predictor_models()

    item = get_item_from_dynamo_db(DYNAMODB_TABLE_NAME, revision)

    logger.info(f"Getting models for revision: {revision}")

    if item is None:
        logger.error(f"No models found for revision: {revision}")
        return ALL_PREDICTOR_MODELS

    for model_name, s3_key in item.items():
        s3_path = Path(s3_key)
        s3_directory = s3_path.parent
        local_file_path = f"predictor/artifacts/{model_name}"
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path, exist_ok=True)
        download_from_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=str(s3_directory / model_name / f"{model_name}.pkl"),
            file_path=os.path.join(local_file_path, f"{model_name}.pkl"),
        )
        download_from_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=str(s3_directory / model_name / PREPROCESSOR_FILE_NAME),
            file_path=os.path.join(str(local_file_path), PREPROCESSOR_FILE_NAME),
        )
        model = MODELS.retrieve(model_name)
        ml_model = model.ml_model()
        ml_model.load(os.path.join(local_file_path, f"{model_name}.pkl"))
        preprocessor = model.preprocessor()
        preprocessor.load(os.path.join(local_file_path, PREPROCESSOR_FILE_NAME))
        ALL_PREDICTOR_MODELS[model_name] = PredictModel(name=model_name, model=ml_model, preprocessor=preprocessor)

    return ALL_PREDICTOR_MODELS


def get_ecs_instance_id() -> str:
    try:
        response = requests.get("http://localhost:51678/v1/metadata")
        metadata = response.json()
        return metadata["ContainerInstanceArn"].split("/")[-1]
    except Exception:
        return "unknown"
