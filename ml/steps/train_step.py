import os

from ml.ml_models.base_ml_model import BaseMLModel
from ml.schemas.feature_target import FeatureTarget
from ml.utils.consts import LOCAL_BASE_ARTIFACT_DIR, S3_BUCKET_NAME
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def train_step(preprocessed: dict[DatasetType, FeatureTarget], ml_model: BaseMLModel, name: str, revision: str) -> BaseMLModel:
    """
    Train the model using the preprocessed datasets.

    Args:
        preprocessed (dict[DatasetType, FeatureTarget]): A dictionary containing the preprocessed datasets.
        ml_model (BaseMLModel): The model to train.
        name (str): The name of the model.
        revision (str): The revision of the model.

    Returns:
        BaseMLModel: The trained model.
    """
    logger.info("Started Train Step.")

    ml_model.train(preprocessed)
    ml_model.save(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(revision, name, f"{name}.pkl"),
        file_path=os.path.join(LOCAL_BASE_ARTIFACT_DIR, f"{name}.pkl"),
    )

    return ml_model
