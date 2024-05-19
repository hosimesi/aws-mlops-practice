import os
from unittest.mock import MagicMock, call, patch

from scipy.sparse import csr_matrix

from ml.schemas.feature_target import FeatureTarget
from ml.schemas.metrics import EvaluateMetrics
from ml.steps.sanity_check_step import sanity_check_step
from ml.utils.consts import DYNAMODB_TABLE_NAME, LOCAL_BASE_ARTIFACT_DIR, S3_BUCKET_NAME
from ml.utils.enums import DatasetType


@patch("ml.steps.sanity_check_step.MODELS")
@patch("ml.steps.sanity_check_step.get_latest_revision_except_current")
@patch("ml.steps.sanity_check_step.download_from_s3")
def tets_sanity_check_step_new_model_win(mocked_downlogd_from_s3, mocked_get_latest_revision_except_current, mocked_MODELS):
    revision = "test_revision"
    name = "test_name"
    preprocessed = {
        DatasetType.TRAIN: FeatureTarget(feature=csr_matrix([[1, 2], [3, 4]]), target=[[0], [1]]),
        DatasetType.VALID: FeatureTarget(feature=csr_matrix([[5, 6], [7, 8]]), target=[[0], [1]]),
        DatasetType.TEST: FeatureTarget(feature=csr_matrix([[9, 10], [11, 12]]), target=[[0], [1]]),
    }

    evaluate_metrics = EvaluateMetrics(
        logloss=0.10536051565782628,
        accuracy=1.0,
        auc=1.0,
        precision=1.0,
        recall=1.0,
        calibration=1.0,
    )

    expected_s3_key = os.path.join(revision, name)

    mocked_get_latest_revision_except_current.return_value = {
        "revision": "previous_revision",
        "s3_keys": {
            name: "s3_key",
        },
    }

    mocked_ml_model = MagicMock()
    mocked_ml_model_instance = mocked_ml_model.reurn_value
    mocked_MODELS.retrieve.return_value.ml_model = mocked_ml_model
    mocked_ml_model_instance.load.return_value = None
    mocked_ml_model_instance.batch_predict.return_value = [0.1, 0.9]

    actual_s3_key = sanity_check_step(
        revision=revision, name=name, preprocessed=preprocessed, evaluate_metrics=evaluate_metrics
    )

    mocked_get_latest_revision_except_current.assert_called_once_with(
        table_name=DYNAMODB_TABLE_NAME, current_revision=revision
    )

    expected_download_from_s3_calls = [
        call(
            s3_bucket=S3_BUCKET_NAME,
            s3_key="s3_key/test_name.pkl",
            file_path=os.path.join(LOCAL_BASE_ARTIFACT_DIR, "test_name.pkl"),
        ),
        call(
            s3_bucket=S3_BUCKET_NAME,
            s3_key="s3_key/preprocessor.pkl",
            file_path=os.path.join(LOCAL_BASE_ARTIFACT_DIR, "preprocessor.pkl"),
        ),
    ]

    mocked_downlogd_from_s3.assert_has_calls(expected_download_from_s3_calls)

    assert actual_s3_key == expected_s3_key
