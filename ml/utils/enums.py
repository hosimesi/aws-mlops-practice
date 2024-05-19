from enum import Enum


class DatasetType(str, Enum):
    TRAIN = "train"
    VALID = "valid"
    TEST = "test"
