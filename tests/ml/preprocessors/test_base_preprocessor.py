import numpy as np
import pytest

from ml.preprocessors.base_preprocessor import BasePreprocessor


class PreprocessorImplement(BasePreprocessor):
    def feature(self):
        raise NotImplementedError

    def target(self):
        raise NotImplementedError

    def transform(self, data: np.ndarray):
        raise NotImplementedError

    def fit_transform(self, data: np.ndarray):
        raise NotImplementedError

    def load(self, file_path: str):
        raise NotImplementedError

    def save(self, file_path: str):
        raise NotImplementedError


def test_target():
    preprocessor = PreprocessorImplement()
    with pytest.raises(NotImplementedError):
        preprocessor.target()


def test_transform():
    preprocessor = PreprocessorImplement()
    data = np.array([[1, 2, 3], [4, 5, 6]])
    with pytest.raises(NotImplementedError):
        preprocessor.transform(data)


def test_fit_transform():
    preprocessor = PreprocessorImplement()
    data = np.array([[1, 2, 3], [4, 5, 6]])
    with pytest.raises(NotImplementedError):
        preprocessor.fit_transform(data)


def test_load():
    preprocessor = PreprocessorImplement()
    file_path = "test_path"
    with pytest.raises(NotImplementedError):
        preprocessor.load(file_path)


def test_save():
    preprocessor = PreprocessorImplement()
    file_path = "test_path"
    with pytest.raises(NotImplementedError):
        preprocessor.save(file_path)
