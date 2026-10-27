"""Data processing module containing hallucinated LLM imports."""

import pandas as pd
import pd_utils  # ❌ Hallucinated package (DepScope flagged)
from np_helpers import array_to_dataframe  # ❌ Hallucinated package
import json


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load JSON data into pandas DataFrame."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)
