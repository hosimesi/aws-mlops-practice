import numpy as np
from sklearn.metrics import (
    accuracy_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ml.ml_models.base_ml_model import BaseMLModel
from ml.schemas.feature_target import FeatureTarget
from ml.schemas.metrics import DataMetrics, EvaluateMetrics
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def evaluate_step(
    preprocessed: dict[DatasetType, FeatureTarget], ml_model: BaseMLModel
) -> tuple[EvaluateMetrics, DataMetrics]:
    """
    Evaluate the model using the preprocessed test dataset.
    Args:
        preprocessed (dict[DatasetType, FeatureTarget]): A dictionary containing the preprocessed datasets.
        ml_model (BaseMLModel): The trained model.
    Returns:
        EvaluateMetrics: An object containing the computed evaluation metrics.
        DataMetrics: An object containing the sizes of the datasets.
    """
    logger.info("Started Evaluate Step.")
    test_data = preprocessed[DatasetType.TEST]
    predictions = np.array(ml_model.batch_predict(test_data.feature))
    pred_bin = np.where(predictions > 0.5, 1, 0)

    logloss = log_loss(test_data.target, predictions)
    accuracy = accuracy_score(test_data.target, pred_bin)
    auc = roc_auc_score(test_data.target, predictions)
    precision = precision_score(test_data.target, pred_bin)
    recall = recall_score(test_data.target, pred_bin)
    calibration = predictions.sum() / test_data.target.sum()

    eval_metrics = EvaluateMetrics(
        logloss=logloss, accuracy=accuracy, auc=auc, precision=precision, recall=recall, calibration=calibration
    )
    logger.info(f"Evaluation Metrics: {eval_metrics}")

    data_metrics = DataMetrics(
        train_data_ammount=preprocessed[DatasetType.TRAIN].feature.shape[0],
        test_data_ammount=test_data.feature.shape[0],
        valid_data_ammount=preprocessed[DatasetType.VALID].feature.shape[0],
    )
    logger.info(f"Data Metrics: {data_metrics}")

    logger.info("Finished Evaluate Step.")

    return eval_metrics, data_metrics
