import unittest
from unittest.mock import MagicMock, patch

from ml.preprocessors.ctr_model_preprocessor import CTRModelPreprocessor


class TestCTRModelPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = CTRModelPreprocessor()
        self.test_data = ["test1", "test2", "test3"]

    @patch("sklearn.feature_extraction.FeatureHasher.transform")
    def test_transform(self, mock_transform):
        mock_transform.return_value = MagicMock()
        transformed_data = self.preprocessor.transform(self.test_data)
        self.assertIsNotNone(transformed_data)
        mock_transform.assert_called_once_with(self.test_data)

    @patch("sklearn.feature_extraction.FeatureHasher.fit_transform")
    def test_fit_transform(self, mock_fit_transform):
        mock_fit_transform.return_value = MagicMock()
        transformed_data = self.preprocessor.fit_transform(self.test_data)
        self.assertIsNotNone(transformed_data)
        mock_fit_transform.assert_called_once_with(self.test_data)

    @patch("pickle.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_save(self, mock_open, mock_pickle_dump):
        file_path = self.preprocessor.save("test_file_path")
        self.assertEqual(file_path, "test_file_path")
        mock_open.assert_called_once_with("test_file_path", "wb")
        mock_pickle_dump.assert_called_once()

    @patch("pickle.load")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_load(self, mock_open, mock_pickle_load):
        mock_pickle_load.return_value = MagicMock()
        self.preprocessor.load("test_file_path")
        self.assertIsNotNone(self.preprocessor.feature_hasher)
        mock_open.assert_called_once_with("test_file_path", "rb")
        mock_pickle_load.assert_called_once()
