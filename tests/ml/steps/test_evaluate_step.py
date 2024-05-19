from unittest.mock import MagicMock

import numpy as np
from scipy.sparse import csr_matrix

from ml.schemas.feature_target import FeatureTarget
from ml.schemas.metrics import DataMetrics, EvaluateMetrics
from ml.steps.evaluate_step import evaluate_step
from ml.utils.enums import DatasetType


def test_evalute_step():
    preprocessed = {
        DatasetType.TRAIN: FeatureTarget(feature=csr_matrix([[1, 2], [3, 4]]), target=np.array([0, 1])),
        DatasetType.VALID: FeatureTarget(feature=csr_matrix([[5, 6], [7, 8]]), target=np.array([0, 1])),
        DatasetType.TEST: FeatureTarget(feature=csr_matrix([[9, 10], [11, 12]]), target=np.array([0, 1])),
    }

    ml_model = MagicMock()

    ml_model.batch_predict.return_value = [0.1, 0.9]

    expected_eval_metrics = EvaluateMetrics(
        logloss=0.10536051565782628,
        accuracy=1.0,
        auc=1.0,
        precision=1.0,
        recall=1.0,
        calibration=1.0,
    )

    expected_data_metrics = DataMetrics(train_data_ammount=2, test_data_ammount=2, valid_data_ammount=2)

    actual_eval_metrics, actual_data_metrics = evaluate_step(preprocessed=preprocessed, ml_model=ml_model)

    assert actual_eval_metrics == expected_eval_metrics
    assert actual_data_metrics == expected_data_metrics
