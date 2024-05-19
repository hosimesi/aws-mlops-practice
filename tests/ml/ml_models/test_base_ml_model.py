from unittest.mock import MagicMock

import pytest
from scipy.sparse._csr import csr_matrix

from ml.ml_models.base_ml_model import BaseMLModel
from ml.schemas.feature_target import FeatureTarget
from ml.utils.enums import DatasetType


class ModelImplement(BaseMLModel):
    def train(self, preprocessed: dict[DatasetType, FeatureTarget]) -> None:
        raise NotImplementedError

    def save(self, s3_bucket: str, s3_key: str, file_path: str) -> str:
        raise NotImplementedError

    def load(self, file_path: str) -> None:
        raise NotImplementedError

    def predict(self, input: csr_matrix) -> float:
        raise NotImplementedError

    def batch_predict(self, input: csr_matrix) -> list[float]:
        raise NotImplementedError


def test_train():
    model = ModelImplement()
    preprocessed = MagicMock()
    with pytest.raises(NotImplementedError):
        model.train(preprocessed)


def test_save():
    model = ModelImplement()
    s3_bucket = "test_bucket"
    s3_key = "test_model"
    file_path = "test_file_path"
    with pytest.raises(NotImplementedError):
        model.save(s3_bucket, s3_key, file_path)


def test_load():
    model = ModelImplement()
    file_path = "test_file_path"
    with pytest.raises(NotImplementedError):
        model.load(file_path)


def test_predict():
    model = ModelImplement()
    input_data = csr_matrix([1, 2, 3])
    with pytest.raises(NotImplementedError):
        model.predict(input_data)


def test_batch_predict():
    model = ModelImplement()
    input_data = csr_matrix([1, 2, 3])
    with pytest.raises(NotImplementedError):
        model.batch_predict(input_data)
