from pydantic import BaseModel, ConfigDict

from app.tools.profiler import DatasetProfiler
from app.tools.registry import ToolRegistry
from app.tools.transformation import (
    filter_data,
    sort_data,
    group_and_aggregate,
)
from app.tools.statistics import (
    calculate_statistics,
    calculate_correlation,
    detect_outliers,
)
from app.tools.contracts import (
    FilterInput,
    SortInput,
    AggregateInput,
    StatisticsInput,
    CorrelationInput,
    OutlierInput,
)


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    profiler = DatasetProfiler()

    registry.register(
        name="profile_dataset",
        description="Generate a structural profile of the current dataset.",
        function=profiler.profile,
        input_model=ProfileInput,
    )

    registry.register(
        name="filter_data",
        description="Filter rows using a supported condition.",
        function=filter_data,
        input_model=FilterInput,
    )


    registry.register(
        name="sort_data",
        description=(
            "Sort the current dataset by an existing column. "
            "The column specified in 'by' must exactly match a column "
            "in the current dataset. After group_and_aggregate, use "
            "the actual output column name, such as 'sum_Total Revenue', "
            "rather than the original column name."
        ),
        function=sort_data,
        input_model=SortInput,
    )

    registry.register(
        name="group_and_aggregate",
        description=(
            "Group rows and calculate an aggregate. "
            "The output contains the grouping column(s) and a generated "
            "aggregation column named '<aggregation>_<target_column>'. "
            "For example, summing 'Total Revenue' produces "
            "'sum_Total Revenue'. Later steps must reference the exact "
            "output column name."
        ),
        function=group_and_aggregate,
        input_model=AggregateInput,
    )


    registry.register(
        name="calculate_statistics",
        description="Calculate descriptive statistics for a numeric column.",
        function=calculate_statistics,
        input_model=StatisticsInput,
    )

    registry.register(
        name="calculate_correlation",
        description="Calculate Pearson correlation between numeric columns.",
        function=calculate_correlation,
        input_model=CorrelationInput,
    )

    registry.register(
        name="detect_outliers",
        description="Detect outliers using the IQR method.",
        function=detect_outliers,
        input_model=OutlierInput,
    )

    return registry
