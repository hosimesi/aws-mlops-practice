import unittest
from unittest.mock import MagicMock, patch

from ml.ml_models.sgd_classifier_ctr_model import SGDClassifierCTRModel
from ml.utils.enums import DatasetType


class TestSGDClassifierCTRModel(unittest.TestCase):
    @patch("ml.ml_models.sgd_classifier_ctr_model.SGDClassifier")
    @patch.object(SGDClassifierCTRModel, "_grid_search")
    def test_train(self, mocked_grid_search, mocked_sgd_classifier):
        mocked_grid_search.return_value = 0.01
        model = SGDClassifierCTRModel()
        preprocessed = {DatasetType.TRAIN: MagicMock(), DatasetType.VALID: MagicMock()}
        model.train(preprocessed)
        self.assertEqual(model.model, mocked_sgd_classifier.return_value)

    @patch("pickle.dump")
    @patch("builtins.open")
    @patch("ml.ml_models.sgd_classifier_ctr_model.upload_to_s3")
    def test_save(self, mocked_upload_to_s3, mocked_open, mocked_pickle_dump):
        model = SGDClassifierCTRModel()
        model.model = MagicMock()
        s3_bucket = "test_bucket"
        s3_key = "test_key"
        file_path = "test_path"
        self.assertEqual(model.save(s3_bucket, s3_key, file_path), file_path)
        mocked_upload_to_s3.assert_called_once_with(s3_bucket=s3_bucket, s3_key=s3_key, file_path=file_path)

    @patch("pickle.load")
    @patch("builtins.open")
    def test_load(self, mocked_open, mocked_pickle_load):
        model = SGDClassifierCTRModel()
        mocked_model = MagicMock()
        mocked_pickle_load.return_value = mocked_model
        model.load("test_path")
        mocked_open.assert_called_once_with("test_path", "rb")
        self.assertEqual(model.model, mocked_model)

    def test_predict(self):
        model = SGDClassifierCTRModel()
        model.model = MagicMock()
        model.model.predict_proba.return_value = [[0.1, 0.9]]
        self.assertEqual(model.predict("test_input"), 0.9)

    def test_batch_predict(self):
        model = SGDClassifierCTRModel()
        model.model = MagicMock()
        model.model.predict_proba.return_value = [[0.1, 0.9], [0.2, 0.8]]
        self.assertEqual(model.batch_predict("test_input"), [0.9, 0.8])
