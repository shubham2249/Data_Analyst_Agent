from app.tools import create_tool_registry
from app.tools.registry import ToolDefinition


def test_registry_contains_expected_tools():
    registry = create_tool_registry()

    tools = registry.list_tools()

    expected_tools = {
        "profile_dataset",
        "filter_data",
        "sort_data",
        "group_and_aggregate",
        "calculate_statistics",
        "calculate_correlation",
        "detect_outliers",
    }

    assert set(tools) == expected_tools
    assert "load_dataset" not in tools


def test_registry_returns_tool_definition():
    registry = create_tool_registry()

    tool = registry.get("profile_dataset")

    assert isinstance(tool, ToolDefinition)
    assert tool.name == "profile_dataset"
    assert callable(tool.function)


def test_registry_describes_tools():
    registry = create_tool_registry()

    descriptions = registry.describe_tools()

    assert isinstance(descriptions, list)
    assert all("name" in tool for tool in descriptions)
    assert all("input_schema" in tool for tool in descriptions)
