import os
from unittest.mock import ANY, MagicMock, patch

import polars as pl

from ml.steps.extract_step import extract_from_redshift_step, extract_step
from ml.utils.consts import LOCAL_BASE_ARTIFACT_DIR, S3_BUCKET_NAME, TRAIN_DATA_FILE_NAME, TRAIN_DATA_S3_PATH
from ml.utils.enums import DatasetType


@patch("polars.read_csv")
@patch("ml.steps.extract_step.upload_to_s3")
@patch("ml.steps.extract_step.download_from_s3")
def test_extract_step(mocked_download_from_s3, mocked_upload_to_s3, mocked_read_csv):
    name = "test_model"
    revision = "test_revision"
    train_args = {DatasetType.TRAIN: 0.6, DatasetType.VALID: 0.2, DatasetType.TEST: 0.2}
    local_file_path = os.path.join(LOCAL_BASE_ARTIFACT_DIR, name, revision)

    mocked_read_csv.return_value = pl.DataFrame(
        {
            "feature1": [1, 2, 3, 4, 5],
            "feature2": [6, 7, 8, 9, 10],
            "target": [0, 1, 0, 1, 0],
        }
    )
    mocked_df = mocked_read_csv.return_value

    mocked_df.write_csv = MagicMock()

    expected_extracted = {
        DatasetType.TRAIN: pl.DataFrame(
            {
                "feature1": [1, 2, 3],
                "feature2": [6, 7, 8],
                "target": [0, 1, 0],
            }
        ),
        DatasetType.VALID: pl.DataFrame(
            {
                "feature1": [4],
                "feature2": [9],
                "target": [1],
            }
        ),
        DatasetType.TEST: pl.DataFrame(
            {
                "feature1": [2],
                "feature2": [7],
                "target": [1],
            }
        ),
    }
    actual_extracted = extract_step(name, revision, train_args)

    mocked_download_from_s3.assert_called_once_with(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(TRAIN_DATA_S3_PATH, TRAIN_DATA_FILE_NAME),
        file_path=os.path.join(local_file_path, "raw_data.tsv"),
    )

    mocked_upload_to_s3.assert_called_with(s3_bucket=S3_BUCKET_NAME, s3_key=ANY, file_path=ANY)

    assert actual_extracted[DatasetType.TRAIN].equals(expected_extracted[DatasetType.TRAIN])
    assert actual_extracted[DatasetType.VALID].equals(expected_extracted[DatasetType.VALID])
    assert actual_extracted[DatasetType.TEST].equals(expected_extracted[DatasetType.TEST])


@patch("ml.steps.extract_step.upload_to_s3")
@patch("ml.steps.extract_step.extract_from_redshift")
def test_extract_from_redshift_step(mocked_extract_from_redshift, mocked_upload_to_s3):
    # Setup
    name = "test_model"
    revision = "test_revision"
    train_args = {DatasetType.TRAIN: 0.6, DatasetType.VALID: 0.2, DatasetType.TEST: 0.2}

    df = MagicMock()
    df.write_csv = MagicMock()
    df.shape = [5, 3]

    mocked_extract_from_redshift.return_value = df

    actual_extracted = extract_from_redshift_step(name, revision, train_args)

    assert mocked_upload_to_s3.call_count == 3
    mocked_upload_to_s3.assert_called_with(s3_bucket=S3_BUCKET_NAME, s3_key=ANY, file_path=ANY)

    for dataset_type in DatasetType:
        assert dataset_type in actual_extracted
