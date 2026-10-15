import json

import numpy as np
import pandas as pd

from app.agent.results import normalize_output


def test_dataframe_output_has_metadata_and_preview():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "region": ["North", "South", "East"],
    })

    result = normalize_output(df)

    assert result["output_type"] == "dataframe"
    assert result["metadata"]["row_count"] == 3
    assert result["metadata"]["column_count"] == 2
    assert result["metadata"]["preview_truncated"] is False
    assert len(result["data"]) == 3


def test_dataframe_preview_is_limited():
    df = pd.DataFrame({"value": range(150)})

    result = normalize_output(df)

    assert len(result["data"]) == 100
    assert result["metadata"]["row_count"] == 150
    assert result["metadata"]["preview_truncated"] is True


def test_missing_and_nonfinite_values_become_null():
    df = pd.DataFrame({
        "value": [1.0, np.nan, np.inf, -np.inf],
    })

    result = normalize_output(df)

    assert result["data"] == [
        {"value": 1.0},
        {"value": None},
        {"value": None},
        {"value": None},
    ]


def test_statistics_output_is_json_serializable():
    result = normalize_output({
        "count": np.int64(3),
        "mean": np.float64(150.5),
        "missing_ratio": float("nan"),
    })

    encoded = json.dumps(result, allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded["data"]["count"] == 3
    assert decoded["data"]["mean"] == 150.5
    assert decoded["data"]["missing_ratio"] is None