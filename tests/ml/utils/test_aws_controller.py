from unittest.mock import patch

import polars as pl
import pytest

from ml.utils import consts
from ml.utils.aws_controller import (
    download_from_s3,
    extract_from_redshift,
    get_item_from_dynamo_db,
    get_latest_model_path_from_s3,
    get_latest_revision_except_current,
    insert_revision_to_dynamo_db,
    update_ecs_service,
    upload_to_s3,
)


@patch("boto3.resource")
def test_upload_to_s3(mocked_resource):
    s3_bucket = "test_bucket"
    s3_key = "test_key"
    file_path = "test_file_path"

    mocked_s3 = mocked_resource.return_value
    mocked_bucket = mocked_s3.Bucket.return_value

    upload_to_s3(s3_bucket=s3_bucket, s3_key=s3_key, file_path=file_path)

    mocked_resource.assert_called_once_with("s3")
    mocked_s3.Bucket.assert_called_once_with(s3_bucket)
    mocked_bucket.upload_file.assert_called_once_with(Key=s3_key, Filename=file_path)


@patch("boto3.resource")
def test_download_from_s3(mocked_resource):
    s3_bucket = "test_bucket"
    s3_key = "test_key"
    file_path = "test_file_path"

    mocked_s3 = mocked_resource.return_value
    mocked_bucket = mocked_s3.Bucket.return_value

    download_from_s3(s3_bucket=s3_bucket, s3_key=s3_key, file_path=file_path)

    mocked_resource.assert_called_once_with("s3")
    mocked_s3.Bucket.assert_called_once_with(s3_bucket)
    mocked_bucket.download_file.assert_called_once_with(Key=s3_key, Filename=file_path)


@patch("boto3.client")
def test_get_latest_model_path_from_s3_is_exist(mocked_client):
    s3_bucket = "test_bucket"
    model_name = "test_model"

    mocked_s3 = mocked_client.return_value
    mocked_s3.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "test_model_1", "LastModified": "2021-01-01"},
            {"Key": "test_model_2", "LastModified": "2021-01-02"},
        ]
    }

    expected = "test_model_2"

    actual = get_latest_model_path_from_s3(s3_bucket=s3_bucket, model_name=model_name)

    assert actual == expected


@patch("boto3.client")
def test_get_latest_model_path_from_s3_is_not_exist(mocked_client):
    s3_bucket = "test_bucket"
    model_name = "test_model"

    mocked_s3 = mocked_client.return_value
    mocked_s3.list_objects_v2.return_value = {"Contents": []}

    with pytest.raises(FileNotFoundError):
        get_latest_model_path_from_s3(s3_bucket=s3_bucket, model_name=model_name)


@patch("boto3.dynamodb.conditions.Key")
@patch("boto3.resource")
def test_get_item_from_dynamo_db_success(mocked_resource, mocked_key):
    dynamodb_table = "test_table"
    revision = "test_revision"

    mocked_dynamodb = mocked_resource.return_value
    mocked_table = mocked_dynamodb.Table.return_value
    mocked_table.query.return_value = {"Items": [{"revision": "test_revision", "s3_keys": {"revision": "test_revision"}}]}
    mocked_key_instance = mocked_key.return_value
    mocked_key_instance.eq.return_value = "test_condition"

    expected = {"revision": "test_revision"}

    actual = get_item_from_dynamo_db(dynamodb_table=dynamodb_table, revision=revision)

    assert actual == expected


@patch("boto3.resource")
def test_get_item_from_dynamo_db_fail(mocked_resource):
    dynamodb_table = "test_table"
    revision = "test_revision"

    mocked_dynamodb = mocked_resource.return_value
    mocked_table = mocked_dynamodb.Table.return_value
    mocked_table.query.side_effect = Exception("test_error")

    expected = None

    actual = get_item_from_dynamo_db(dynamodb_table=dynamodb_table, revision=revision)

    assert actual == expected


@patch("boto3.resource")
def test_insert_revision_to_dynamo_db(mocked_resource):
    dynamodb_table = "test_table"
    revision = "test_revision"
    s3_keys = {"test_key": "test_value"}
    logged_at = "test_logged_at"

    mocked_dynamodb = mocked_resource.return_value
    mocked_table = mocked_dynamodb.Table.return_value
    mocked_table.put_item.return_value = None

    insert_revision_to_dynamo_db(dynamodb_table=dynamodb_table, revision=revision, s3_keys=s3_keys, logged_at=logged_at)

    mocked_resource.assert_called_once_with("dynamodb")
    mocked_dynamodb.Table.assert_called_once_with(dynamodb_table)
    mocked_table.put_item.assert_called_once_with(Item={"revision": revision, "s3_keys": s3_keys, "logged_at": logged_at})


@patch("boto3.resource")
def test_get_latest_revision_except_current_success(mocked_resource):
    table_name = "test_table"
    current_revision = "test_current_revision"

    mocked_dynamodb = mocked_resource.return_value
    mocked_table = mocked_dynamodb.Table.return_value
    mocked_table.scan.return_value = {"Items": [{"revision": "test_revision"}]}

    expected = {"revision": "test_revision"}

    actual = get_latest_revision_except_current(table_name=table_name, current_revision=current_revision)

    assert actual == expected


@patch("boto3.resource")
def test_get_latest_revision_except_current_fail(mocked_resource):
    table_name = "test_table"
    current_revision = "test_current_revision"

    mocked_dynamodb = mocked_resource.return_value
    mocked_table = mocked_dynamodb.Table.return_value
    mocked_table.scan.side_effect = Exception("test_error")

    expected = None

    actual = get_latest_revision_except_current(table_name=table_name, current_revision=current_revision)

    assert actual == expected


@patch("boto3.client")
def test_update_ecs_service_success(mocked_client):
    cluster = "test_cluster"
    service = "test_service"

    mocked_ecs = mocked_client.return_value
    mocked_ecs.update_service.return_value = None

    update_ecs_service(cluster=cluster, service=service)

    mocked_client.assert_called_once_with("ecs")
    mocked_ecs.update_service.assert_called_once_with(cluster=cluster, service=service, forceNewDeployment=True)


@patch("boto3.client")
def test_extract_from_redshift_success(mocked_client):
    sql = "test_sql"

    mocked_redshift = mocked_client.return_value
    mocked_redshift.execute_statement.return_value = {"Id": "test_id"}

    mocked_redshift.describe_statement.return_value = {
        "Status": "FINISHED",
    }

    mocked_redshift.get_statement_result.return_value = {
        "Records": [
            [{"stringValue": "test_id"}, {"stringValue": "test_hour"}],
            [{"stringValue": "test_id"}, {"stringValue": "test_hour"}],
        ]
    }

    expected_df = pl.DataFrame(
        {
            "id": ["test_id", "test_id"],
            "hour": ["test_hour", "test_hour"],
        }
    )

    actual_df = extract_from_redshift(sql=sql)

    mocked_client.assert_called_once_with("redshift-data")
    mocked_redshift.execute_statement.assert_called_once_with(
        WorkgroupName=consts.REDSHIFT_WORKGROUP,
        Database=consts.REDSHIFT_DATABASE,
        Sql=sql,
    )
    mocked_redshift.describe_statement.assert_called_once_with(Id="test_id")
    mocked_redshift.get_statement_result.assert_called_once_with(Id="test_id")

    assert actual_df.equals(expected_df)


@patch("boto3.client")
def test_extract_from_redshift_fail(mocked_client):
    sql = "test_sql"

    mocked_redshift = mocked_client.return_value
    mocked_redshift.execute_statement.return_value = {"Id": "test_id"}

    mocked_redshift.describe_statement.return_value = {
        "Status": "FAILED",
    }

    actual_df = extract_from_redshift(sql=sql)

    assert actual_df is None
