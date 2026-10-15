import pandas as pd
import pytest

from app.tools.transformation import (
    DataAnalysisError,
    filter_data,
    sort_data,
    group_and_aggregate,
)
from app.tools.statistics import (
    calculate_statistics,
    calculate_correlation,
    detect_outliers,
)


@pytest.fixture
def sales_df():
    return pd.DataFrame({
        "region": ["North", "South", "North", "South", "East"],
        "revenue": [100.0, 200.0, 150.0, 250.0, 1000.0],
        "quantity": [1, 2, 3, 4, 5],
    })


def test_filter_data(sales_df):
    result = filter_data(
        sales_df, "revenue", "greater_than", 150
    )

    assert result["revenue"].tolist() == [200.0, 250.0, 1000.0]


def test_filter_rejects_unknown_operator(sales_df):
    with pytest.raises(DataAnalysisError):
        filter_data(sales_df, "revenue", "execute_code", 100)


def test_sort_data(sales_df):
    result = sort_data(sales_df, "revenue", ascending=False)

    assert result["revenue"].iloc[0] == 1000.0


def test_group_and_aggregate(sales_df):
    result = group_and_aggregate(
        sales_df, "region", "revenue", "mean"
    )

    north = result.loc[result["region"] == "North", "mean_revenue"].iloc[0]
    assert north == 125.0


def test_calculate_statistics(sales_df):
    result = calculate_statistics(sales_df, "revenue")

    assert result["count"] == 5
    assert result["mean"] == 340.0
    assert result["median"] == 200.0


def test_calculate_correlation(sales_df):
    result = calculate_correlation(
        sales_df, "revenue", "quantity"
    )

    assert -1.0 <= result["pearson_correlation"] <= 1.0
    assert result["paired_observations"] == 5


def test_detect_outliers(sales_df):
    result = detect_outliers(sales_df, "revenue")

    assert result["revenue"].tolist() == [1000.0]


def test_reject_missing_column(sales_df):
    with pytest.raises(DataAnalysisError):
        calculate_statistics(sales_df, "profit")