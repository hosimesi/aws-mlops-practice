import pickle

import numpy as np
from scipy.sparse._csr import csr_matrix
from sklearn.feature_extraction import FeatureHasher

from ml.preprocessors.base_preprocessor import BasePreprocessor
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


class CTRModelPreprocessor(BasePreprocessor):
    def __init__(self) -> None:
        self._features = [
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
        ]
        self._target = "click"
        self.feature_hasher = FeatureHasher(n_features=2**18, input_type="string")

    @property
    def feature(self) -> list[str]:
        return self._features

    @property
    def target(self) -> str:
        return self._target

    def transform(self, data: np.ndarray) -> csr_matrix:
        logger.info("Started CTR Model Preprocessor.")
        hashed_feature = self.feature_hasher.transform(data)

        logger.info("Finished CTR Model Preprocessor.")
        return hashed_feature

    def fit_transform(self, data: np.ndarray) -> csr_matrix:
        logger.info("Started CTR Model Preprocessor.")
        hashed_feature = self.feature_hasher.fit_transform(data)

        logger.info("Finished CTR Model Preprocessor.")
        return hashed_feature

    def load(self, file_path: str) -> None:
        with open(file_path, "rb") as f:
            self.feature_hasher = pickle.load(f)

    def save(self, file_path: str) -> str:
        with open(file_path, "wb") as f:
            pickle.dump(self.feature_hasher, f)
        return file_path
