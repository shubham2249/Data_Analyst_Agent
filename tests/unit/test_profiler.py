import pandas as pd

from app.tools.profiler import DatasetProfiler


def test_dataset_profiler():

    df = pd.DataFrame(
        {
            "name": ["A", "B", "C"],
            "age": [20, 21, 22],
            "city": ["Delhi", "Mumbai", "Delhi"],
        }
    )

    profiler = DatasetProfiler()
    profile = profiler.profile(df)

    assert profile.rows == 3
    assert profile.columns == 3

    assert profile.numeric_columns == ["age"]

    assert "name" in profile.categorical_columns
    assert "city" in profile.categorical_columns

    assert profile.duplicate_rows == 0