from pydantic import BaseModel


class EvaluateMetrics(BaseModel):
    logloss: float
    accuracy: float
    auc: float
    precision: float
    recall: float
    calibration: float


class DataMetrics(BaseModel):
    train_data_ammount: int
    test_data_ammount: int
    valid_data_ammount: int
