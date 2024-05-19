import datetime as dt
import os

NAME = os.getenv("NAME")
if not NAME:
    raise ValueError("NAME is not set.")

JST = dt.timezone(dt.timedelta(hours=+9), "JST")
TRAIN_DATA_S3_PATH = "train_data"
TRAIN_DATA_FILE_NAME = "train.tsv"
S3_BUCKET_NAME = f"{NAME}-mlops-practice"
LOCAL_BASE_ARTIFACT_DIR = "ml/artifacts"
DYNAMODB_TABLE_NAME = f"{NAME}-mlops-practice"
PREDICTOR_ECS_CLUSTER = f"{NAME}-mlops-practice-ecs"

PREDCITOR_ECS_SERVICE = f"{NAME}-predictor-service"
PREDICTOR_CANARY_ECS_SERVICE = f"{NAME}-predictor-canary-service"
PREDICTOR_ECS_SERVICES = [PREDCITOR_ECS_SERVICE]
# PREDICTOR_ECS_SERVICES = [PREDCITOR_ECS_SERVICE, PREDICTOR_CANARY_ECS_SERVICE]

INTERNAL_NAMESPACE = f"{NAME}-mlops-practice.internal"
PREPROCESSOR_FILE_NAME = "preprocessor.pkl"


REDSHIFT_CLUSTER_IDENTIFIER = f"{NAME}-mlops-practice"
REDSHIFT_DATABASE = "dev"
REDSHIFT_USER = "admin"

REDSHIFT_WORKGROUP = f"{NAME}-workgroup"
