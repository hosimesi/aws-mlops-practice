import os
from unittest.mock import MagicMock

from ml.schemas.feature_target import FeatureTarget
from ml.steps.train_step import train_step
from ml.utils.consts import LOCAL_BASE_ARTIFACT_DIR, S3_BUCKET_NAME
from ml.utils.enums import DatasetType


def test_train_step():
    # Setup
    mocked_ml_model_instance = MagicMock()
    mocked_ml_model_instance.train = MagicMock()
    mocked_ml_model_instance.save = MagicMock()
    preprocessed = {
        DatasetType.TRAIN: FeatureTarget(feature=MagicMock(), target=MagicMock()),
        DatasetType.VALID: FeatureTarget(feature=MagicMock(), target=MagicMock()),
        DatasetType.TEST: FeatureTarget(feature=MagicMock(), target=MagicMock()),
    }
    name = "test_model"
    revision = "test_revision"
    # Call the function under test
    result = train_step(preprocessed, mocked_ml_model_instance, name, revision)  # Update this line
    # Assertions
    mocked_ml_model_instance.train.assert_called_once_with(preprocessed)
    mocked_ml_model_instance.save.assert_called_once_with(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(revision, name, f"{name}.pkl"),
        file_path=os.path.join(LOCAL_BASE_ARTIFACT_DIR, f"{name}.pkl"),
    )
    assert result == mocked_ml_model_instance
