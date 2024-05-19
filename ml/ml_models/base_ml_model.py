from abc import ABC, abstractmethod

from scipy.sparse._csr import csr_matrix

from ml.schemas.feature_target import FeatureTarget
from ml.utils.enums import DatasetType


class BaseMLModel(ABC):
    @abstractmethod
    def train(self, preprocessed: dict[DatasetType, FeatureTarget]) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self, s3_bucket: str, s3_key: str, file_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def load(self, file_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, input: csr_matrix) -> float:
        raise NotImplementedError

    @abstractmethod
    def batch_predict(self, input: csr_matrix) -> list[float]:
        raise NotImplementedError
