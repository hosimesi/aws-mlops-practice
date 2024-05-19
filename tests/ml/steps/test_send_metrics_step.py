from unittest.mock import patch

import polars as pl

from ml.schemas.metrics import DataMetrics, EvaluateMetrics
from ml.steps.send_metrics_step import send_metrics_step
from ml.utils.enums import DatasetType


@patch("os.getenv")
@patch("ml.steps.send_metrics_step.push_to_gateway")
@patch("ml.steps.send_metrics_step.Gauge")
def test_send_metrics_step(mocked_gauge, mocked_push_to_gateway, mocked_getenv):
    # Setup
    mocked_getenv.return_value = "local"
    current_time_jst = "2022-01-01"
    eval_metrics = EvaluateMetrics(logloss=0.1, accuracy=0.2, auc=0.3, precision=0.4, recall=0.5, calibration=0.6)
    data_metrics = DataMetrics(train_data_ammount=100, valid_data_ammount=50, test_data_ammount=30)
    model_name = "test_model"
    extracted = {
        DatasetType.TRAIN: pl.DataFrame(
            {
                "column1": ["value1", "value2", "value1"],
            }
        ),
        DatasetType.VALID: pl.DataFrame(
            {
                "column1": ["value1", "value2", "value1"],
            }
        ),
        DatasetType.TEST: pl.DataFrame(
            {
                "column1": ["value1", "value2", "value1"],
            }
        ),
    }
    # Call the function under test
    send_metrics_step(current_time_jst, eval_metrics, data_metrics, model_name, extracted)
    # Assertions
    mocked_getenv.assert_called_once_with("SYSTEM_ENV")
    assert mocked_gauge.call_count == 3
    assert mocked_push_to_gateway.call_count == 1
