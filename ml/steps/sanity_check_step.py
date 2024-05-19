import os
from typing import Any

from scipy.sparse._csr import csr_matrix
from sklearn.metrics import log_loss

from ml.models.models import MODELS
from ml.schemas.metrics import EvaluateMetrics
from ml.utils.aws_controller import download_from_s3, get_latest_revision_except_current
from ml.utils.consts import DYNAMODB_TABLE_NAME, LOCAL_BASE_ARTIFACT_DIR, PREPROCESSOR_FILE_NAME, S3_BUCKET_NAME
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def sanity_check_step(
    revision: str, name: str, preprocessed: dict[DatasetType, csr_matrix], evaluate_metrics: EvaluateMetrics
) -> str:
    logger.info("Started Sanity Check Step.")
    item: dict[str, Any] | None = get_latest_revision_except_current(table_name=DYNAMODB_TABLE_NAME, current_revision=revision)
    s3_path = os.path.join(revision, name)

    if not item:
        logger.info("No previous revision found. Skipping sanity check.")
        return s3_path

    if "s3_keys" not in item.keys():
        logger.info("No previous revision found. Skipping sanity check.")
        return s3_path

    if name not in item["s3_keys"].keys():
        logger.info("No previous revision found. Skipping sanity check.")
        return s3_path

    logger.info(f"Previous revision found: {item['revision']}")
    logger.info(f"Downloading model and preprocessor from S3 for revision: {item['revision']}")
    download_from_s3(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(item["s3_keys"][name], f"{name}.pkl"),
        file_path=os.path.join(LOCAL_BASE_ARTIFACT_DIR, f"{name}.pkl"),
    )
    download_from_s3(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(item["s3_keys"][name], PREPROCESSOR_FILE_NAME),
        file_path=os.path.join(LOCAL_BASE_ARTIFACT_DIR, PREPROCESSOR_FILE_NAME),
    )
    logger.info("Model and preprocessor downloaded successfully.")

    logger.info("Loading model and preprocessor.")
    model = MODELS.retrieve(name=name)
    ml_model_instance = model.ml_model()
    ml_model_instance.load(os.path.join(LOCAL_BASE_ARTIFACT_DIR, f"{name}.pkl"))

    logger.info("Model and preprocessor loaded successfully.")

    logger.info("Predicting test data.")
    predictions = ml_model_instance.batch_predict(input=preprocessed[DatasetType.TEST].feature)

    logger.info("Calculating evaluation metrics.")
    logloss = log_loss(preprocessed[DatasetType.TEST].target, predictions)

    logger.info("Evaluation metrics calculated.")

    # Compare the new model with the old model by logloss.
    if logloss < evaluate_metrics.logloss:
        logger.warning("New model is worse than the old model.")
        logger.warning(f"Old Model Metrics: {logloss}, New Model Metrics: {evaluate_metrics}")
        return item["s3_keys"][name]
    else:
        logger.info("New model is better than the old model.")
        logger.info(f"Old Model Metrics: {logloss}, New Model Metrics: {evaluate_metrics}")
        return s3_path
