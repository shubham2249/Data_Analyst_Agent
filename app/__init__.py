from app.tools.ingestion import DatasetIngestion
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


def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    ingestion = DatasetIngestion()
    profiler = DatasetProfiler()

    registry.register(
        "profile_dataset",
        "Inspect dataset structure and quality.",
        profiler.profile,
        StatisticsInput,
    )  # Temporary compatibility note below

    registry.register(
        "filter_data",
        "Filter dataset rows using a supported condition.",
        filter_data,
        FilterInput,
    )

    registry.register(
        "sort_data",
        "Sort rows by a column.",
        sort_data,
        SortInput,
    )

    registry.register(
        "group_and_aggregate",
        "Group rows and calculate an aggregation.",
        group_and_aggregate,
        AggregateInput,
    )

    registry.register(
        "calculate_statistics",
        "Calculate descriptive statistics for a numeric column.",
        calculate_statistics,
        StatisticsInput,
    )

    registry.register(
        "calculate_correlation",
        "Calculate Pearson correlation between two numeric columns.",
        calculate_correlation,
        CorrelationInput,
    )

    registry.register(
        "detect_outliers",
        "Find IQR-based outliers in a numeric column.",
        detect_outliers,
        OutlierInput,
    )

    return registry