from ml.utils.aws_controller import get_item_from_dynamo_db, insert_revision_to_dynamo_db
from ml.utils.consts import DYNAMODB_TABLE_NAME
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def create_model_revision_step(revision: str, name: str, s3_path: str) -> None:
    """Create a new model revision and update the DynamoDB table.
    Args:
        revision (str): The revision of the model.
        name (str): The name of the model.
        s3_path (str): The S3 path of the model.

    Returns:
        None
    """

    item = get_item_from_dynamo_db(dynamodb_table=DYNAMODB_TABLE_NAME, revision=revision)
    logger.info(f"Updating item in DynamoDB: {item}")

    if item:
        s3_keys = item.copy()
        s3_keys[name] = s3_path
        logger.info(f"Updated item in DynamoDB: {item}")
    else:
        s3_keys = {name: s3_path}
    logged_at = revision
    insert_revision_to_dynamo_db(dynamodb_table=DYNAMODB_TABLE_NAME, revision=revision, s3_keys=s3_keys, logged_at=logged_at)
