from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any]


class FilterInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str = Field(min_length=1, max_length=200)
    operator: Literal[
        "equals",
        "not_equals",
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "contains",
    ]
    value: str | int | float | bool | None


class SortInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    by: str = Field(min_length=1, max_length=200)
    ascending: bool = True


class AggregateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_by: str | list[str]
    target_column: str = Field(min_length=1, max_length=200)
    aggregation: Literal["sum", "mean", "median", "min", "max", "count"]


class StatisticsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str = Field(min_length=1, max_length=200)


class CorrelationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_a: str = Field(min_length=1, max_length=200)
    column_b: str = Field(min_length=1, max_length=200)


class OutlierInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str = Field(min_length=1, max_length=200)