"""Optional ML model placeholder for future stretch implementation."""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations

import pandas as pd


def predict_risk(df: pd.DataFrame) -> pd.Series:
    """Return placeholder probabilities so pipeline remains stable without training."""
    if df.empty:
        return pd.Series(dtype=float)
    return pd.Series([0.0] * len(df), index=df.index)
