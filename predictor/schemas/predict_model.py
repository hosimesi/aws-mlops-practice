from dataclasses import dataclass

from ml.ml_models.base_ml_model import BaseMLModel
from ml.preprocessors.base_preprocessor import BasePreprocessor


@dataclass
class PredictModel:
    name: str
    preprocessor: BasePreprocessor
    model: BaseMLModel
