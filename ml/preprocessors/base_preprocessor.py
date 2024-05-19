from abc import ABC, abstractmethod

import numpy as np
from scipy.sparse._csr import csr_matrix


class BasePreprocessor(ABC):
    @property
    @abstractmethod
    def feature(self) -> list[str]:
        raise NotImplementedError

    @property
    def target(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def transform(self, data: np.ndarray) -> csr_matrix:
        raise NotImplementedError

    @abstractmethod
    def fit_transform(self, data: np.ndarray) -> csr_matrix:
        raise NotImplementedError

    @abstractmethod
    def load(self, file_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self, file_path: str) -> str:
        raise NotImplementedError
