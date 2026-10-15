
from dataclasses import dataclass, field

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)


@dataclass
class DatasetProfile:
    rows: int
    columns: int
    column_names: list[str]
    numeric_columns: list[str] = field(default_factory=list)
    categorical_columns: list[str] = field(default_factory=list)
    datetime_columns: list[str] = field(default_factory=list)
    missing_values: dict[str, int] = field(default_factory=dict)
    duplicate_rows: int = 0


class DatasetProfiler:
    def profile(self, df: pd.DataFrame) -> DatasetProfile:
        numeric_columns = []
        categorical_columns = []
        datetime_columns = []

        for column in df.columns:
            dtype = df[column].dtype

            if is_datetime64_any_dtype(dtype):
                datetime_columns.append(column)
            elif is_bool_dtype(dtype):
                categorical_columns.append(column)
            elif is_numeric_dtype(dtype):
                numeric_columns.append(column)
            elif (
                is_object_dtype(dtype)
                or is_string_dtype(dtype)
                or isinstance(dtype, pd.CategoricalDtype)
            ):
                categorical_columns.append(column)

        missing_values = {
            column: int(count)
            for column, count in df.isna().sum().items()
            if count > 0
        }

        return DatasetProfile(
            rows=len(df),
            columns=len(df.columns),
            column_names=df.columns.tolist(),
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            datetime_columns=datetime_columns,
            missing_values=missing_values,
            duplicate_rows=int(df.duplicated().sum()),
        )