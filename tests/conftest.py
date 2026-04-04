from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def simple_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ds": pd.date_range("2024-01-01", periods=64, freq="D"),
            "y": np.linspace(10.0, 30.0, 64),
        }
    )
