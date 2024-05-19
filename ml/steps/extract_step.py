import os

import polars as pl

from ml.utils.aws_controller import download_from_s3, extract_from_redshift, upload_to_s3
from ml.utils.consts import LOCAL_BASE_ARTIFACT_DIR, S3_BUCKET_NAME, TRAIN_DATA_FILE_NAME, TRAIN_DATA_S3_PATH
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def extract_step(name: str, revision: str, train_args: dict[DatasetType, float]) -> dict[DatasetType, pl.DataFrame]:
    """
    Extracts data based on the provided model configuration and saves the extracted data locally and on S3.

    Parameters:
        name (str): The name of the model.
        revision (str): The revision of the model.
        train_args (dict[DatasetType, float]): The data split arguments for each dataset type.

    Returns:
        dict[DatasetType, pl.DataFrame]:
            dictionary containing the extracted data.
            The keys are DatasetType enum members and the values are DataFrames.
    """

    logger.info(f"Starting extract_step for model: {name},revision: {revision}")

    local_file_path = os.path.join(LOCAL_BASE_ARTIFACT_DIR, name, revision)
    if not os.path.exists(local_file_path):
        os.makedirs(local_file_path, exist_ok=True)

    logger.info(f"Downloading data from S3 bucket: {S3_BUCKET_NAME}, key: {TRAIN_DATA_S3_PATH}/{TRAIN_DATA_FILE_NAME}")
    download_from_s3(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(TRAIN_DATA_S3_PATH, TRAIN_DATA_FILE_NAME),
        file_path=os.path.join(local_file_path, "raw_data.tsv"),
    )
    logger.info("Data downloaded successfully")

    df = pl.read_csv(os.path.join(local_file_path, "raw_data.tsv"), separator="\t")

    if df is None:
        raise ValueError("Failed to read CSV file.")

    extracted: dict[DatasetType, pl.DataFrame] = {}
    num_rows = df.shape[0]
    start = 0

    for dataset_type in DatasetType:
        logger.info(f"Extracting data for dataset type: {dataset_type}")
        data_interval = train_args[dataset_type]
        split_point = int(num_rows * data_interval)
        extract_df = df.slice(start, split_point)
        start = split_point
        logger.info(f"Extracted data for dataset type: {dataset_type}. shape: {extract_df.shape}")
        logger.info(f"Writing extracted data to csv: {local_file_path}/{dataset_type.value}_extracted.csv")

        saved_file_name = f"{dataset_type.value}_extracted.csv"
        df.write_csv(os.path.join(local_file_path, saved_file_name), separator=",")

        upload_to_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, saved_file_name),
            file_path=os.path.join(local_file_path, saved_file_name),
        )

        extracted[dataset_type] = extract_df
        logger.info(f"Data extraction completed for dataset type: {dataset_type}")

    logger.info("All data extraction completed")
    return extracted


def extract_from_redshift_step(
    name: str, revision: str, train_args: dict[DatasetType, float]
) -> dict[DatasetType, pl.DataFrame]:
    """Extracts data from Redshift based on the provided model configuration.
    Args:
        name (str): The name of the model.
        revision (str): The revision of the model.
        train_args (dict[DatasetType, float]): The data split arguments for each dataset type.

    Returns:
        dict[DatasetType, pl.DataFrame]:
            dictionary containing the extracted data.
            The keys are DatasetType enum members and the values are DataFrames.
    """
    logger.info(f"Starting extract_from_redshift_step for model: {name}, revision: {revision}")

    with open("ml/sqls/extract.sql") as f:
        sql = f.read()

    df = extract_from_redshift(sql=sql)

    if df is None:
        raise ValueError("Failed to extract data from Redshift.")

    local_file_path = os.path.join(LOCAL_BASE_ARTIFACT_DIR, name, revision)
    if not os.path.exists(local_file_path):
        os.makedirs(local_file_path, exist_ok=True)
    extracted: dict[DatasetType, pl.DataFrame] = {}
    num_rows = df.shape[0]
    start = 0

    for dataset_type in DatasetType:
        logger.info(f"Extracting data for dataset type: {dataset_type}")
        data_interval = train_args[dataset_type]
        split_point = int(num_rows * data_interval)
        extract_df = df.slice(start, split_point)
        start = split_point
        logger.info(f"Extracted data for dataset type: {dataset_type}. shape: {extract_df.shape}")
        logger.info(f"Writing extracted data to csv: {local_file_path}/{dataset_type.value}_extracted.csv")

        saved_file_name = f"{dataset_type.value}_extracted.csv"
        df.write_csv(os.path.join(local_file_path, saved_file_name), separator=",")

        upload_to_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, saved_file_name),
            file_path=os.path.join(local_file_path, saved_file_name),
        )

        extracted[dataset_type] = extract_df
        logger.info(f"Data extraction completed for dataset type: {dataset_type}")

    logger.info("All data extraction completed")
    return extracted
