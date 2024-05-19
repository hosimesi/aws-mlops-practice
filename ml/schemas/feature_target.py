from dataclasses import dataclass

import polars as pl
from scipy.sparse import csr_matrix


@dataclass
class FeatureTarget:
    feature: csr_matrix
    target: pl.series.series.Series
