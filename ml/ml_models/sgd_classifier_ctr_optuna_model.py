import pickle

import optuna
from scipy.sparse import csr_matrix
from sklearn.linear_model import SGDClassifier

from ml.ml_models.base_ml_model import BaseMLModel
from ml.schemas.feature_target import FeatureTarget
from ml.utils.aws_controller import upload_to_s3
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


class SGDClassifierCTROptunaModel(BaseMLModel):
    def __init__(self) -> None:
        self.name = "sgd_classifier_ctr_optuna_model"
        self.model: SGDClassifier = None

    def _optuna_search(self, preprocessed: dict[DatasetType, FeatureTarget]) -> float:
        def objective(trial: optuna.trial._trial.Trial) -> float:
            max_alpha = 0.1
            alpha = trial.suggest_float("alpha", 0, max_alpha)
            model = SGDClassifier(loss="log_loss", penalty="l2", random_state=42, alpha=alpha)

            model.fit(preprocessed[DatasetType.TRAIN].feature, preprocessed[DatasetType.TRAIN].target)
            score = model.score(preprocessed[DatasetType.VALID].feature, preprocessed[DatasetType.VALID].target)

            logger.info(f"aplha: {alpha} | valid logloss: {score}")
            return float(score)

        logger.info("Started Hyper Parameter (alpha) tuning.")
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=10)
        best_alpha = study.best_params
        return float(best_alpha["alpha"])

    def train(self, preprocessed: dict[DatasetType, FeatureTarget]) -> None:
        logger.info("Started SGD Classifier CTR Optuna Model train.")

        logger.info("Started Optuna Hyperparmeter Tuning Search.")
        best_alpha = self._optuna_search(preprocessed=preprocessed)
        logger.info("Finished Optuna Hyperparmeter Tuning Search.")

        logger.info("Started train SGDClassifier.")
        self.model = SGDClassifier(loss="log_loss", penalty="l2", random_state=42, alpha=best_alpha)
        self.model.fit(preprocessed[DatasetType.TRAIN].feature, preprocessed[DatasetType.TRAIN].target)
        logger.info("Finished train SGDClassifier.")

        logger.info("Finished SGD Classifier CTR Optuna Model train.")

    def save(self, s3_bucket: str, s3_key: str, file_path: str) -> str:
        logger.info(f"Save {self.name} as {file_path}.")
        with open(file_path, "wb") as f:
            pickle.dump(self.model, f)
        upload_to_s3(s3_bucket=s3_bucket, s3_key=s3_key, file_path=file_path)
        return file_path

    def load(self, file_path: str) -> None:
        logger.info(f"Load {self.name} as {file_path}.")
        with open(file_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, input: str) -> float:
        return float(self.model.predict_proba(input)[0][1])

    def batch_predict(self, input: csr_matrix) -> list[float]:
        return [float(x[1]) for x in self.model.predict_proba(input)]
