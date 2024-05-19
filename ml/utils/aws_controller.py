import datetime as dt
import time

import boto3
import polars as pl

from ml.utils import consts
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def upload_to_s3(s3_bucket: str, s3_key: str, file_path: str) -> None:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3_bucket)

    logger.info(f"Start uploading model file: {s3_key}, file_path: {file_path}")
    bucket.upload_file(Key=s3_key, Filename=file_path)
    logger.info(f"Completely uploaded model file: {s3_key}, file_path: {file_path}")


def download_from_s3(s3_bucket: str, s3_key: str, file_path: str) -> None:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3_bucket)

    logger.info(f"Start downloading model file: {s3_key}, file_path: {file_path}")
    bucket.download_file(Key=s3_key, Filename=file_path)
    logger.info(f"Completely downloaded model file: {s3_key}, file_path: {file_path}")


def get_latest_model_path_from_s3(s3_bucket: str, model_name: str) -> str:
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=s3_bucket)

    if "Contents" not in response:
        raise FileNotFoundError(f"No model found in S3 bucket: {s3_bucket} with prefix: {model_name}")
    model_objects = [obj for obj in response["Contents"] if model_name in obj["Key"]]
    if not model_objects:
        raise FileNotFoundError(f"No model found in S3 bucket: {s3_bucket} with model name: {model_name}")
    latest_model = max(model_objects, key=lambda x: x["LastModified"])
    return latest_model["Key"]


def get_item_from_dynamo_db(dynamodb_table: str, revision: str) -> dict[str, str] | None:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(dynamodb_table)

    if not revision:
        logger.info(f"Getting the latest revision from DynamoDB table: {dynamodb_table}")
        try:
            response = table.scan()
            if "Items" in response:
                items = response["Items"]
                latest_revision = max(items, key=lambda x: x["revision"])
                return latest_revision["s3_keys"]
        except Exception as e:
            logger.error(f"Failed to get the latest revision from DynamoDB table: {dynamodb_table}, error: {str(e)}")

    logger.info(f"Getting revision: {revision} from DynamoDB table: {dynamodb_table}")
    try:
        response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("revision").eq(revision))
        if "Items" in response:
            return response["Items"][0]["s3_keys"]
    except Exception as e:
        logger.error(f"Failed to get items with revision: {revision} from DynamoDB table: {dynamodb_table}, error: {str(e)}")
    return None


def insert_revision_to_dynamo_db(dynamodb_table: str, revision: str, s3_keys: dict[str, str], logged_at: str | None) -> None:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(dynamodb_table)

    logger.info(f"Inserting revision: {revision} to DynamoDB table: {dynamodb_table}. Records: {s3_keys}")
    try:
        if not logged_at:
            logged_at = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        response = table.put_item(Item={"revision": revision, "s3_keys": s3_keys, "logged_at": logged_at})
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.info(f"Inserted revision: {revision} to DynamoDB table: {dynamodb_table}")
        else:
            logger.error(f"Failed to insert revision: {revision} to DynamoDB table: {dynamodb_table}. Records: {s3_keys}")
    except Exception:
        logger.error(f"Failed to insert revision: {revision} to DynamoDB table: {dynamodb_table}. Records: {s3_keys}")


def get_latest_revision_except_current(table_name: str, current_revision: str) -> dict[str, str] | None:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    try:
        # テーブルから全てのレコードを取得
        response = table.scan()
    except Exception as e:
        logger.error(f"Failed to get items from DynamoDB table: {table_name}, error: {str(e)}")
        return None
    else:
        items = response["Items"]

        if not items:
            return None

        # 現在のrevisionを除く
        items_except_current = [item for item in items if item["revision"] != current_revision]
        revisions = [item["revision"] for item in items if item["revision"] != current_revision]

        if not revisions:
            logger.info(f"Revisions except current: {revisions}")
            return None

        # revisionが最新のレコードを取得
        latest_item = max(items_except_current, key=lambda item: item["revision"])

        return latest_item


def update_ecs_service(cluster: str, service: str) -> None:
    ecs = boto3.client("ecs")
    logger.info(f"Start updating ECS service: {service} in cluster: {cluster}")
    try:
        response = ecs.update_service(cluster=cluster, service=service, forceNewDeployment=True)
        logger.info(f"Started ECS service update: {response}")
    except Exception as e:
        logger.error(f"Failed to update ECS service: {service} in cluster: {cluster}, error: {str(e)}")


def extract_from_redshift(sql: str) -> pl.DataFrame | None:
    column_names = [
        "id",
        "hour",
        "C1",
        "banner_pos",
        "site_id",
        "site_domain",
        "site_category",
        "app_id",
        "app_domain",
        "app_category",
        "device_id",
        "device_ip",
        "device_model",
        "device_type",
        "device_conn_type",
        "C14",
        "C15",
        "C16",
        "C17",
        "C18",
        "C19",
        "C20",
        "C21",
        "click",
    ]

    logger.info("Start executing SQL")
    try:
        client = boto3.client("redshift-data")
        response = client.execute_statement(
            WorkgroupName=consts.REDSHIFT_WORKGROUP,
            Database=consts.REDSHIFT_DATABASE,
            Sql=sql,
        )

        logger.info(f"Sent SQL to Redshift. Id: {response['Id']}")
        while True:
            logger.info(f"Waiting for the SQL to finish. Id: {response['Id']}")
            status_description = client.describe_statement(Id=response["Id"])
            logger.info(f"SQL execution status: {status_description}")
            status = status_description["Status"]
            logger.info(f"SQL execution status: {status}")
            if status == "FINISHED":
                logger.info(f"SQL execution finished. Id: {response['Id']}")
                results = client.get_statement_result(Id=response["Id"])
                records = results["Records"]
                data_dicts = [
                    {column_names[i]: field.get("stringValue") or field.get("longValue") for i, field in enumerate(record)}
                    for record in records
                ]
                return pl.DataFrame(data_dicts)
            elif status == "FAILED":
                raise Exception(f"Failed to execute SQL: {sql}")
            time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to extract data from Redshift with SQL: {sql}, error: {str(e)}")
    return None
