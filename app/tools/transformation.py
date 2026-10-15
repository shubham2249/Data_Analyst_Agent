
from typing import Any

import pandas as pd


class DataAnalysisError(ValueError):
    """Raised when a requested data operation is invalid."""


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        raise DataAnalysisError(f"Unknown columns: {missing}")


def filter_data(
    df: pd.DataFrame,
    column: str,
    operator: str,
    value: Any,
) -> pd.DataFrame:
    _require_columns(df, [column])

    series = df[column]

    if operator == "equals":
        mask = series == value
    elif operator == "not_equals":
        mask = series != value
    elif operator == "greater_than":
        mask = series > value
    elif operator == "greater_than_or_equal":
        mask = series >= value
    elif operator == "less_than":
        mask = series < value
    elif operator == "less_than_or_equal":
        mask = series <= value
    elif operator == "contains":
        mask = series.astype("string").str.contains(
            str(value), case=False, na=False, regex=False
        )
    else:
        raise DataAnalysisError(f"Unsupported operator: {operator}")

    return df.loc[mask.fillna(False)].copy()


def sort_data(
    df: pd.DataFrame,
    by: str,
    ascending: bool = True,
) -> pd.DataFrame:
    _require_columns(df, [by])

    return df.sort_values(
        by=by,
        ascending=ascending,
        na_position="last",
    ).copy()


def group_and_aggregate(
    df: pd.DataFrame,
    group_by: str | list[str],
    target_column: str,
    aggregation: str,
) -> pd.DataFrame:
    groups = [group_by] if isinstance(group_by, str) else group_by

    if not groups:
        raise DataAnalysisError("At least one grouping column is required.")

    _require_columns(df, groups + [target_column])

    allowed_aggregations = {
        "sum", "mean", "median", "min", "max", "count"
    }

    if aggregation not in allowed_aggregations:
        raise DataAnalysisError(
            f"Unsupported aggregation: {aggregation}"
        )

    if aggregation != "count" and not pd.api.types.is_numeric_dtype(
        df[target_column]
    ):
        raise DataAnalysisError(
            f"Column '{target_column}' must be numeric for {aggregation}."
        )

    result = (
        df.groupby(groups, dropna=False)[target_column]
        .agg(aggregation)
        .reset_index(name=f"{aggregation}_{target_column}")
    )

    return result