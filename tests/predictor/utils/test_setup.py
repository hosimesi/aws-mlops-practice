from enum import Enum
from unittest.mock import MagicMock, patch

from predictor.utils.setup import get_ecs_instance_id, get_predictor_models

mocked_model1 = MagicMock()
mocked_model2 = MagicMock()
mocked_model1.name = "model1"
mocked_model2.name = "model2"

mocked_model1.ml_model = MagicMock()
mocked_model1_ml_model_instance = mocked_model1.ml_model.return_value
mocked_model2.ml_model = MagicMock()
mocked_model2_ml_model_instance = mocked_model2.ml_model.return_value

mocked_model1_ml_model_instance.load = MagicMock()
mocked_model2_ml_model_instance.load = MagicMock()

mocked_model1.preprocessor = MagicMock()
mocked_model1_preprocessor_instance = mocked_model1.preprocessor.return_value
mocked_model2.preprocessor = MagicMock()
mocked_model2_preprocessor_instance = mocked_model2.preprocessor.return_value

mocked_model1_preprocessor_instance.load = MagicMock()
mocked_model2_preprocessor_instance.load = MagicMock()


class MockedModels(Enum):
    MODEL1 = mocked_model1
    MODEL2 = mocked_model2

    @classmethod
    def retrieve(cls, name):
        return cls[name.upper()].value


@patch("os.makedirs")
@patch("os.path.exists")
@patch("predictor.utils.setup.download_from_s3")
@patch("predictor.utils.setup.get_latest_model_path_from_s3")
@patch("predictor.utils.setup.MODELS", MockedModels)
def test_get_latest_predictor_models_dir_not_exists(mocked_latest_model_path, mocked_download, mocked_exists, mocked_makedirs):
    mocked_exists.side_effect = [False, True]

    result = get_predictor_models()

    mocked_makedirs.assert_called_once()
    mocked_download.assert_called()

    mocked_model1_ml_model_instance.load.assert_called_once()
    mocked_model1_preprocessor_instance.load.assert_called_once()
    mocked_model2_ml_model_instance.load.assert_called_once()
    mocked_model2_preprocessor_instance.load.assert_called_once()
    assert isinstance(result, dict)


@patch("os.makedirs")
@patch("os.path.exists")
@patch("predictor.utils.setup.download_from_s3")
@patch("predictor.utils.setup.get_latest_model_path_from_s3")
@patch("predictor.utils.setup.MODELS", MockedModels)
def test_get_latest_predictor_models_dir_is_exists(mocked_latest_model_path, mocked_download, mocked_exists, mocked_makedirs):
    mocked_exists.side_effect = [True, True]

    result = get_predictor_models()

    mocked_makedirs.assert_not_called()
    mocked_download.assert_called()

    mocked_model1_ml_model_instance.load.assert_called()
    mocked_model1_preprocessor_instance.load.assert_called()
    mocked_model2_ml_model_instance.load.assert_called()
    mocked_model2_preprocessor_instance.load.assert_called()
    assert isinstance(result, dict)


@patch("os.makedirs")
@patch("os.path.exists")
@patch("predictor.utils.setup.download_from_s3")
@patch("predictor.utils.setup.get_item_from_dynamo_db")
@patch("predictor.utils.setup.MODELS", MockedModels)
def test_get_version_predictor_models(mocked_get_item, mocked_download, mocked_exists, mocked_makedirs):
    mocked_exists.side_effect = [False, True]
    mocked_get_item.return_value = {"model1": "model1_key", "model2": "model2_key"}

    result = get_predictor_models(revision="test")

    mocked_makedirs.assert_called_once()
    mocked_download.assert_called()
    mocked_model1_ml_model_instance.load.assert_called()
    mocked_model1_preprocessor_instance.load.assert_called()
    mocked_model2_ml_model_instance.load.assert_called()
    mocked_model2_preprocessor_instance.load.assert_called()
    assert isinstance(result, dict)


@patch("requests.get")
def test_get_ecs_instance_id(mocked_get):
    class MockedResponse:
        def json(self):
            return {"ContainerInstanceArn": "arn/test/instance_id"}

    mocked_get.return_value = MockedResponse()
    result = get_ecs_instance_id()
    assert result == "instance_id"


@patch("requests.get")
def test_get_ecs_instance_id_exception(mocked_get):
    mocked_get.side_effect = Exception
    result = get_ecs_instance_id()
    assert result == "unknown"
