import argparse
import datetime as dt
import os

from ml.features.revision import get_current_revision
from ml.models.models import MODELS
from ml.steps import (
    extract_step,
    preprocess_step,
    train_step,
)
from ml.utils.consts import JST
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def load_options() -> argparse.Namespace:
    description = """
    Train ML Pipeline runtime arguments
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-c", "--current_time_jst", type=str, default=dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
    parser.add_argument("-m", "--model_name", type=str, default=os.getenv("MODEL", "sgd_classifier_ctr_model"))

    return parser.parse_args()


def main() -> None:
    args = load_options()
    logger.info(f"Started ML Training. model_name: {args.model_name}")

    revision = get_current_revision(current_time_jst=args.current_time_jst)

    logger.info(f"Current revision: {revision}")

    model_info = MODELS.retrieve(args.model_name)

    logger.info(f"Model name: {model_info.name}")
    logger.info(f"Model Info: {model_info}")

    s3_path = os.path.join(revision, model_info.name)

    logger.info(f"Model s3 path: {s3_path}")

    extracted = extract_step(name=model_info.name, revision=revision, train_args=model_info.train_args)

    logger.info(f"Extracted data: {extracted}")

    preprocessed = preprocess_step(
        extracted=extracted,
        preprocessor=model_info.preprocessor(),
        revision=revision,
        name=model_info.name,
    )

    logger.info(f"Preprocessed data: {preprocessed}")

    ml_model = train_step(preprocessed=preprocessed, ml_model=model_info.ml_model(), revision=revision, name=model_info.name)

    logger.info(f"Trained model: {ml_model}")

    logger.info(f"Finished ML Training. model_name: {args.model_name}")


if __name__ == "__main__":
    main()
