from unittest.mock import patch

from ml.steps.create_model_revision_step import create_model_revision_step
from ml.utils.consts import DYNAMODB_TABLE_NAME


@patch("ml.steps.create_model_revision_step.insert_revision_to_dynamo_db")
@patch("ml.steps.create_model_revision_step.get_item_from_dynamo_db")
def test_create_model_revision_step_item_exist(mocked_get_item_from_dynamo_db, mocked_insert_revision_to_dynamo_db):
    revision = "2021-01-01-00-00-00"
    name = "test_model"
    s3_path = "s3://test_bucket/test_model"

    s3_keys = {name: s3_path}
    expected_s3_keys = s3_keys.copy()
    expected_s3_keys[name] = s3_path
    logged_at = revision

    mocked_get_item_from_dynamo_db.return_value = {name: s3_path}

    create_model_revision_step(revision=revision, name=name, s3_path=s3_path)

    mocked_get_item_from_dynamo_db.assert_called_once_with(dynamodb_table=DYNAMODB_TABLE_NAME, revision=revision)
    mocked_insert_revision_to_dynamo_db.assert_called_once_with(
        dynamodb_table=DYNAMODB_TABLE_NAME, revision=revision, s3_keys=expected_s3_keys, logged_at=logged_at
    )


@patch("ml.steps.create_model_revision_step.insert_revision_to_dynamo_db")
@patch("ml.steps.create_model_revision_step.get_item_from_dynamo_db")
def test_create_model_revision_step_item_not_exist(mocked_get_item_from_dynamo_db, mocked_insert_revision_to_dynamo_db):
    revision = "2021-01-01-00-00-00"
    name = "test_model"
    s3_path = "s3://test_bucket/test_model"

    mocked_get_item_from_dynamo_db.return_value = None

    create_model_revision_step(revision=revision, name=name, s3_path=s3_path)

    mocked_get_item_from_dynamo_db.assert_called_once_with(dynamodb_table=DYNAMODB_TABLE_NAME, revision=revision)
    mocked_insert_revision_to_dynamo_db.assert_called_once_with(
        dynamodb_table=DYNAMODB_TABLE_NAME, revision=revision, s3_keys={name: s3_path}, logged_at=revision
    )
