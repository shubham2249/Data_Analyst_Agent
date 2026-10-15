import pandas as pd

from app.agent.executor import ToolExecutor
from app.tools import create_tool_registry


def test_execute_profile_tool():
    registry = create_tool_registry()
    executor = ToolExecutor(registry)

    df = pd.DataFrame(
        {
            "name": ["A", "B"],
            "age": [20, 25],
        }
    )

    result = executor.execute(
        tool_name="profile_dataset",
        arguments={},
        context={"df": df},
    )

    assert result.rows == 2
    assert result.columns == 2
    assert "name" in result.column_names
    assert "age" in result.column_names
