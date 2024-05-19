import os

import polars as pl
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from ml.schemas.metrics import DataMetrics, EvaluateMetrics
from ml.utils.consts import INTERNAL_NAMESPACE
from ml.utils.enums import DatasetType
from ml.utils.logger.logger_config import get_logger

logger = get_logger(__name__)


def send_metrics_step(
    current_time_jst: str,
    eval_metrics: EvaluateMetrics,
    data_metrics: DataMetrics,
    model_name: str,
    extracted: dict[DatasetType, pl.DataFrame],
) -> None:
    logger.info("Starting send_metrics_step function...")
    if os.getenv("SYSTEM_ENV") == "local":
        pushgateway_url = "pushgateway:9091"
    else:
        pushgateway_url = f"pushgateway.{INTERNAL_NAMESPACE}:9091"

    registry = CollectorRegistry()
    data_distribution = Gauge(
        "data_distribution", "Data distribution", ["dataset", "model_name", "column", "value", "time"], registry=registry
    )
    data_amount = Gauge("data_amount", "Data amount", ["dataset", "model_name", "time"], registry=registry)
    evaluate_metrics_gauge = Gauge("evaluate_metrics", "Evaluate metrics", ["model_name", "metric", "time"], registry=registry)

    for dataset_type in DatasetType:
        df = extracted[dataset_type]
        for column in df.columns:
            value_counts = df[column].value_counts()
            for idx in range(len(value_counts)):
                value = value_counts[column][idx]
                count = value_counts["count"][idx]
                data_distribution.labels(
                    dataset=dataset_type.value, model_name=model_name, column=column, value=str(value), time=current_time_jst
                ).set(count)
        if dataset_type == DatasetType.TRAIN:
            amount = data_metrics.train_data_ammount
        elif dataset_type == DatasetType.VALID:
            amount = data_metrics.valid_data_ammount
        else:
            amount = data_metrics.test_data_ammount

        data_amount.labels(dataset=dataset_type.value, model_name=model_name, time=current_time_jst).set(amount)

    logger.info(f"Sent data distribution and amount metrics for {model_name}")
    # Send evaluation metrics
    for metric, value in eval_metrics.model_dump().items():
        evaluate_metrics_gauge.labels(model_name=model_name, metric=metric, time=current_time_jst).set(value)

    logger.info(f"Sent evaluation metrics for {model_name}")
    # Push metrics to Pushgateway
    push_to_gateway(pushgateway_url, job="ml_pipeline", registry=registry)
    logger.info("Successfully pushed metrics to Pushgateway")
