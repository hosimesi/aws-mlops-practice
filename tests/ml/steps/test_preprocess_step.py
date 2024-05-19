import os
from unittest.mock import MagicMock, call, patch

import polars as pl
from scipy.sparse import csr_matrix

from ml.schemas.feature_target import FeatureTarget
from ml.steps.preprocess_step import preprocess_step
from ml.utils.consts import LOCAL_BASE_ARTIFACT_DIR, PREPROCESSOR_FILE_NAME, S3_BUCKET_NAME
from ml.utils.enums import DatasetType


@patch("builtins.open")
@patch("ml.steps.preprocess_step.upload_to_s3")
@patch("os.makedirs")
@patch("pickle.dump")
def test_preprocess_step(mocked_pickle_dump, mocked_makedirs, mocked_upload_to_s3, mocked_open):
    extracted = {
        DatasetType.TRAIN: pl.DataFrame(pl.DataFrame({"feature": [1, 2], "target": [0, 1]})),
        DatasetType.VALID: pl.DataFrame(pl.DataFrame({"feature": [3, 4], "target": [0, 1]})),
        DatasetType.TEST: pl.DataFrame(pl.DataFrame({"feature": [5, 6], "target": [0, 1]})),
    }
    name = "test_name"
    revision = "test_revision"

    preprocessor = MagicMock()
    preprocessor.feature = ["feature"]
    preprocessor.target = "target"
    preprocessor.transform.return_value = csr_matrix([[1, 2], [3, 4]])
    preprocessor.fit_transform.return_value = csr_matrix([[1, 2], [3, 4]])

    expected_preprocessed = {
        DatasetType.TRAIN: FeatureTarget(feature=csr_matrix([[1, 2], [3, 4]]), target=[[0], [1]]),
        DatasetType.VALID: FeatureTarget(feature=csr_matrix([[1, 2], [3, 4]]), target=[[0], [1]]),
        DatasetType.TEST: FeatureTarget(feature=csr_matrix([[1, 2], [3, 4]]), target=[[0], [1]]),
    }
    local_file_path = os.path.join(LOCAL_BASE_ARTIFACT_DIR, name, revision)

    expected_calls = [
        call(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, f"{DatasetType.TRAIN.value}_preprocessed.pkl"),
            file_path=os.path.join(local_file_path, f"{DatasetType.TRAIN.value}_preprocessed.pkl"),
        ),
        call(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, f"{DatasetType.VALID.value}_preprocessed.pkl"),
            file_path=os.path.join(local_file_path, f"{DatasetType.VALID.value}_preprocessed.pkl"),
        ),
        call(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, f"{DatasetType.TEST.value}_preprocessed.pkl"),
            file_path=os.path.join(local_file_path, f"{DatasetType.TEST.value}_preprocessed.pkl"),
        ),
        call(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, PREPROCESSOR_FILE_NAME),
            file_path=os.path.join(local_file_path, PREPROCESSOR_FILE_NAME),
        ),
    ]

    actual_preprocessed = preprocess_step(extracted=extracted, name=name, revision=revision, preprocessor=preprocessor)

    mocked_upload_to_s3.assert_has_calls(expected_calls, any_order=True)
    for dataset_type in DatasetType:
        assert (
            actual_preprocessed[dataset_type].feature.toarray() == expected_preprocessed[dataset_type].feature.toarray()
        ).all()
        assert (actual_preprocessed[dataset_type].target == expected_preprocessed[dataset_type].target).all()
