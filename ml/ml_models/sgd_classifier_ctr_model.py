import pickle

from scipy.sparse import csr_matrix
from sklearn.linear_model import SGDClassifier

from ml.ml_models.base_ml_model import BaseMLModel
from ml.schemas.feature_target import FeatureTarget
from ml.utils.aws_controller import upload_to_s3
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


class SGDClassifierCTRModel(BaseMLModel):
    def __init__(self) -> None:
        self.name = "sgd_classifier_ctr_model"
        self.model: SGDClassifier = None

    def _grid_search(self, preprocessed: dict[DatasetType, FeatureTarget]) -> float:
        logger.info("Started Grid Search.")
        best_score = 1e10
        best_alpha = 0.01
        for alpha in [1e-5, 1e-4, 1e-3, 1e2, 1e-1]:
            model = SGDClassifier(loss="log_loss", penalty="l2", random_state=42, alpha=alpha)
            model.fit(preprocessed[DatasetType.TRAIN].feature, preprocessed[DatasetType.TRAIN].target)
            score = model.score(preprocessed[DatasetType.VALID].feature, preprocessed[DatasetType.VALID].target)
            logger.info(f"Grid Search| alpha: {alpha}, score: {score}")
            if score < best_score:
                logger.info(f"Best score is updated as {score}")
                best_score = score
                best_alpha = alpha
        logger.info(f"Best alpha: {best_alpha}")
        logger.info("Finished Grid Search.")
        return best_alpha

    def train(self, preprocessed: dict[DatasetType, FeatureTarget]) -> None:
        logger.info("Started SGD Classifier CTR Model train.")

        best_alpha = self._grid_search(preprocessed=preprocessed)

        self.model = SGDClassifier(loss="log_loss", penalty="l2", random_state=42, alpha=best_alpha)
        self.model.fit(preprocessed[DatasetType.TRAIN].feature, preprocessed[DatasetType.TRAIN].target)

        logger.info("Finished SGD Classifier CTR Model train.")

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
