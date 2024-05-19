import os
from unittest.mock import patch

import pytest

from importer.main import handler


@pytest.fixture
def env_vars():
    os.environ["REDSHIFT_WORKGROUP"] = "test_workgroup"
    os.environ["REDSHIFT_DATABASE"] = "test_database"
    os.environ["LAMBDA_IAM_ROLE_ARN"] = "test_arn"
    yield
    del os.environ["REDSHIFT_WORKGROUP"]
    del os.environ["REDSHIFT_DATABASE"]
    del os.environ["LAMBDA_IAM_ROLE_ARN"]


sql = """
COPY imp_log
FROM 's3://{bucket}/{file_path}'
GZIP
IAM_ROLE '{lambda_iam_role_arn}'
FORMAT AS CSV DELIMITER '\\t'
REGION 'ap-northeast-1';
"""


@patch("importer.main.boto3.client")
def test_handler(mock_client, env_vars):
    event = {"Records": [{"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "test-file.csv"}}}]}
    context = {}
    mock_client.return_value.execute_statement.return_value = {"status": "success"}

    handler(event, context)
    mock_client.assert_called_once_with("redshift-data")
    mock_client.return_value.execute_statement.assert_called_once_with(
        WorkgroupName="test_workgroup",
        Database="test_database",
        Sql=sql.format(bucket="test-bucket", lambda_iam_role_arn="test_arn", file_path="test-file.csv"),
    )
