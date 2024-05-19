import os
from typing import Any

import boto3

sql = """
COPY imp_log
FROM 's3://{bucket}/{file_path}'
GZIP
IAM_ROLE '{lambda_iam_role_arn}'
FORMAT AS CSV DELIMITER '\\t'
REGION 'ap-northeast-1';
"""


def handler(event: Any, context: Any) -> None:
    redshift_workgroup = os.getenv("REDSHIFT_WORKGROUP")
    redshift_db = os.getenv("REDSHIFT_DATABASE")
    lambda_iam_role_arn = os.getenv("LAMBDA_IAM_ROLE_ARN")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    file_path = event["Records"][0]["s3"]["object"]["key"]

    full_sql = sql.format(bucket=bucket, lambda_iam_role_arn=lambda_iam_role_arn, file_path=file_path)

    client = boto3.client("redshift-data")
    response = client.execute_statement(
        WorkgroupName=redshift_workgroup,
        Database=redshift_db,
        Sql=full_sql,
    )

    print(response)
