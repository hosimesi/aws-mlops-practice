from ml.utils.aws_controller import update_ecs_service
from ml.utils.consts import PREDICTOR_ECS_CLUSTER, PREDICTOR_ECS_SERVICES
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    for ecs_service in PREDICTOR_ECS_SERVICES:
        logger.info(f"Restarting {ecs_service}")
        update_ecs_service(cluster=PREDICTOR_ECS_CLUSTER, service=ecs_service)
        logger.info(f"Restarted {ecs_service}")
    logger.info("Finished Update Server.")


if __name__ == "__main__":
    main()
