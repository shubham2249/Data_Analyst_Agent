
import pandas as pd

from app.tools.transformation import DataAnalysisError, _require_columns


def calculate_statistics(
    df: pd.DataFrame,
    column: str,
) -> dict[str, float | int | None]:
    _require_columns(df, [column])

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise DataAnalysisError(f"Column '{column}' must be numeric.")

    values = df[column].dropna()

    if values.empty:
        raise DataAnalysisError(
            f"Column '{column}' has no valid numeric values."
        )

    return {
        "count": int(values.count()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()) if len(values) > 1 else None,
        "min": float(values.min()),
        "max": float(values.max()),
    }


def calculate_correlation(
    df: pd.DataFrame,
    column_a: str,
    column_b: str,
) -> dict[str, float | int]:
    _require_columns(df, [column_a, column_b])

    for column in (column_a, column_b):
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise DataAnalysisError(
                f"Column '{column}' must be numeric."
            )

    paired = df[[column_a, column_b]].dropna()

    if len(paired) < 2:
        raise DataAnalysisError(
            "At least two complete pairs are required."
        )

    if paired[column_a].nunique() < 2 or paired[column_b].nunique() < 2:
        raise DataAnalysisError(
            "Correlation is undefined for a constant column."
        )

    correlation = paired[column_a].corr(paired[column_b])

    return {
        "column_a": column_a,
        "column_b": column_b,
        "paired_observations": len(paired),
        "pearson_correlation": float(correlation),
    }


def detect_outliers(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    _require_columns(df, [column])

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise DataAnalysisError(f"Column '{column}' must be numeric.")

    values = df[column].dropna()

    if values.empty:
        raise DataAnalysisError(
            f"Column '{column}' has no valid numeric values."
        )

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    mask = (
        (df[column] < lower_bound)
        | (df[column] > upper_bound)
    )

    return df.loc[mask.fillna(False)].copy()