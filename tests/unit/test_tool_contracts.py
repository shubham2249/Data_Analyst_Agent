import pytest
from pydantic import ValidationError

from app.tools.contracts import FilterInput, AggregateInput


def test_filter_accepts_supported_operator():
    request = FilterInput(
        column="revenue",
        operator="greater_than",
        value=100,
    )

    assert request.column == "revenue"


def test_filter_rejects_unknown_operator():
    with pytest.raises(ValidationError):
        FilterInput(
            column="revenue",
            operator="run_python",
            value=100,
        )


def test_filter_rejects_extra_fields():
    with pytest.raises(ValidationError):
        FilterInput(
            column="revenue",
            operator="equals",
            value=100,
            execute_code="malicious",
        )


def test_aggregate_rejects_unknown_operation():
    with pytest.raises(ValidationError):
        AggregateInput(
            group_by="region",
            target_column="revenue",
            aggregation="drop_database",
        )