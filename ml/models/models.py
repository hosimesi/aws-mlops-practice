from dataclasses import dataclass
from enum import Enum

from ml.ml_models import SGDClassifierCTRModel, SGDClassifierCTROptunaModel
from ml.ml_models.base_ml_model import BaseMLModel
from ml.preprocessors import BasePreprocessor, CTRModelPreprocessor
from ml.utils.enums import DatasetType


@dataclass(frozen=True)
class Model:
    name: str
    train_args: dict[DatasetType, float]
    ml_model: type[BaseMLModel]
    preprocessor: type[BasePreprocessor]


class MODELS(Enum):
    sgd_classifier_ctr_model = Model(
        name="sgd_classifier_ctr_model",
        train_args={
            DatasetType.TRAIN: 0.8,
            DatasetType.VALID: 0.1,
            DatasetType.TEST: 0.1,
        },
        preprocessor=CTRModelPreprocessor,
        ml_model=SGDClassifierCTRModel,
    )
    sgd_classifier_ctr_optuna_model = Model(
        name="sgd_classifier_ctr_optuna_model",
        train_args={
            DatasetType.TRAIN: 0.8,
            DatasetType.VALID: 0.1,
            DatasetType.TEST: 0.1,
        },
        preprocessor=CTRModelPreprocessor,
        ml_model=SGDClassifierCTROptunaModel,
    )

    @staticmethod
    def retrieve(name: str) -> Model:
        for model in [v.value for v in MODELS.__members__.values()]:
            if model.name == name:
                return model
        raise ValueError(f"{name} is not implemented.")
