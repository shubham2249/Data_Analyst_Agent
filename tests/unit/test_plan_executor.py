import pandas as pd

from app.agent.plan_executor import PlanExecutor
from app.tools import create_tool_registry


def test_plan_executes_steps_sequentially():
    dataframe = pd.DataFrame(
        {
            "region": ["North", "South", "North"],
            "revenue": [100, 200, 300],
        }
    )

    plan = {
        "goal": "Calculate revenue statistics above 100",
        "steps": [
            {
                "step_id": "filter_revenue",
                "tool_name": "filter_data",
                "arguments": {
                    "column": "revenue",
                    "operator": "greater_than",
                    "value": 100,
                },
            },
            {
                "step_id": "revenue_statistics",
                "tool_name": "calculate_statistics",
                "arguments": {
                    "column": "revenue",
                },
            },
        ],
    }

    executor = PlanExecutor(create_tool_registry())
    result = executor.execute(plan, dataframe)

    assert result.status == "completed"
    assert len(result.steps) == 2
    assert all(step.status == "completed" for step in result.steps)

    statistics = result.steps[1].output['data']

    assert statistics["count"] == 2
    assert statistics["mean"] == 250.0
    assert result.final_dataframe["revenue"].tolist() == [200, 300]


def test_plan_stops_when_a_step_fails():
    dataframe = pd.DataFrame(
        {
            "region": ["North", "South"],
            "revenue": [100, 200],
        }
    )

    plan = {
        "goal": "Run statistics on a nonexistent column",
        "steps": [
            {
                "step_id": "invalid_statistics",
                "tool_name": "calculate_statistics",
                "arguments": {
                    "column": "missing_column",
                },
            },
            {
                "step_id": "should_not_run",
                "tool_name": "sort_data",
                "arguments": {
                    "by": "revenue",
                    "ascending": True,
                },
            },
        ],
    }

    executor = PlanExecutor(create_tool_registry())
    result = executor.execute(plan, dataframe)

    assert result.status == "failed"
    assert len(result.steps) == 1
    assert result.steps[0].status == "failed"
    assert result.steps[0].step_id == "invalid_statistics"
    assert result.steps[0].error is not None