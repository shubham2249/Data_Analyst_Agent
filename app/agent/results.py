import math
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel


MAX_PREVIEW_ROWS = 100


def to_json_safe(value: Any) -> Any:
    """Convert common Python, Pandas, and NumPy values to JSON-safe values."""

    if value is None or value is pd.NA or value is pd.NaT:
        return None

    if isinstance(value, BaseModel):
        return to_json_safe(value.model_dump(mode="python"))

    if is_dataclass(value) and not isinstance(value, type):
        return to_json_safe(asdict(value))

    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()

    if isinstance(value, np.generic):
        return to_json_safe(value.item())

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, (str, int, bool)):
        return value

    raise TypeError(
        f"Unsupported output type: {type(value).__name__}"
    )


def normalize_output(value: Any) -> dict[str, Any]:
    """Return a consistent, JSON-safe representation of a tool result."""

    if isinstance(value, pd.DataFrame):
        preview = value.head(MAX_PREVIEW_ROWS)
        preview = preview.astype(object).where(
            pd.notna(preview), None
        )

        return {
            "output_type": "dataframe",
            "data": to_json_safe(preview.to_dict(orient="records")),
            "metadata": {
                "row_count": len(value),
                "column_count": len(value.columns),
                "columns": [str(column) for column in value.columns],
                "preview_rows": len(preview),
                "preview_truncated": len(value) > MAX_PREVIEW_ROWS,
            },
        }

    if isinstance(value, pd.Series):
        return {
            "output_type": "series",
            "data": to_json_safe(value.tolist()),
            "metadata": {
                "row_count": len(value),
                "name": str(value.name) if value.name is not None else None,
            },
        }

    return {
        "output_type": type(value).__name__,
        "data": to_json_safe(value),
        "metadata": {},
    }