import os
import pickle

import numpy as np
import polars as pl
from scipy.sparse import csr_matrix

from ml.preprocessors import BasePreprocessor
from ml.schemas.feature_target import FeatureTarget
from ml.utils.aws_controller import upload_to_s3
from ml.utils.consts import LOCAL_BASE_ARTIFACT_DIR, PREPROCESSOR_FILE_NAME, S3_BUCKET_NAME
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def preprocess_step(
    extracted: dict[DatasetType, pl.DataFrame],
    name: str,
    revision: str,
    preprocessor: BasePreprocessor,
) -> dict[DatasetType, FeatureTarget]:
    """
    Apply pre-processing steps to the extracted datasets and save the preprocessed data locally and on S3.

    Parameters:
        extracted (dict[DatasetType, pl.DataFrame]):
            A dictionary containing the extracted datasets.
            The keys are DatasetType enum members and the values are DataFrames.
        name (str): The name of the model.
        revision (str): The revision of the model.
        preprocessor (BasePreprocessor): The preprocessor object.

    Returns:
        dict[DatasetType, FeatureTarget]:
            A dictionary containing the preprocessed datasets.
            The keys are DatasetType enum members and the values are FeatureTarget objects.
    """

    logger.info("Started Appling Model Preprocessor.")
    preprocessed: dict[DatasetType, csr_matrix] = {}
    for dataset_type, extracted_df in extracted.items():
        local_file_path = os.path.join(LOCAL_BASE_ARTIFACT_DIR, name, revision)
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path, exist_ok=True)

        # Select features and target before converting to ndarray
        features_df = extracted_df.select(preprocessor.feature).fill_nan("").fill_null(value="")
        target_df = extracted_df.select(preprocessor.target)

        # Convert to ndarray
        features = np.array(features_df.select(pl.all().cast(str)))
        target = np.array(target_df.select(pl.all().cast(int)))

        if dataset_type == DatasetType.TRAIN:
            sparsed_array = preprocessor.fit_transform(features)
        else:
            sparsed_array = preprocessor.transform(features)

        preprocessed[dataset_type] = FeatureTarget(sparsed_array, target)
        saved_file_name = f"{dataset_type.value}_preprocessed.pkl"
        with open(os.path.join(local_file_path, saved_file_name), "wb") as f:
            pickle.dump(FeatureTarget(sparsed_array, target), f)

        upload_to_s3(
            s3_bucket=S3_BUCKET_NAME,
            s3_key=os.path.join(revision, name, saved_file_name),
            file_path=os.path.join(local_file_path, saved_file_name),
        )

    # Save the pipeline
    with open(os.path.join(local_file_path, PREPROCESSOR_FILE_NAME), "wb") as f:
        pickle.dump(preprocessor, f)

    upload_to_s3(
        s3_bucket=S3_BUCKET_NAME,
        s3_key=os.path.join(revision, name, PREPROCESSOR_FILE_NAME),
        file_path=os.path.join(local_file_path, PREPROCESSOR_FILE_NAME),
    )

    logger.info("Finished Model Preprocessor.")
    return preprocessed
