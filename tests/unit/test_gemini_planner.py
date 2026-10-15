from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from app.agent.gemini_planner import GeminiPlanner, PlannerError
from app.agent.validator import PlanValidator
from app.tools import create_tool_registry


@pytest.fixture
def dataframe():
    return pd.DataFrame(
        {
            "region": ["North", "South", "North"],
            "revenue": [100.0, 200.0, 150.0],
        }
    )


@pytest.fixture
def planner():
    registry = create_tool_registry()
    validator = PlanValidator(registry)

    client = Mock()
    return GeminiPlanner(
        registry=registry,
        validator=validator,
        client=client,
    ), client


def test_valid_plan_is_returned(planner, dataframe):
    gemini_planner, client = planner

    client.models.generate_content.return_value = SimpleNamespace(
        parsed={
            "goal": "Calculate revenue statistics",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "calculate_statistics",
                    "arguments": {"column": "revenue"},
                }
            ],
        },
        text=None,
    )

    result = gemini_planner.create_plan(
        "Calculate statistics for revenue",
        dataframe,
    )

    assert result.goal == "Calculate revenue statistics"
    assert len(result.steps) == 1
    assert result.steps[0].tool_name == "calculate_statistics"
    assert result.steps[0].arguments == {"column": "revenue"}
    client.models.generate_content.assert_called_once()


def test_empty_question_is_rejected_without_api_call(planner, dataframe):
    gemini_planner, client = planner

    with pytest.raises(PlannerError, match="analysis question"):
        gemini_planner.create_plan("   ", dataframe)

    client.models.generate_content.assert_not_called()


def test_malformed_json_is_rejected(planner, dataframe):
    gemini_planner, client = planner

    client.models.generate_content.return_value = SimpleNamespace(
        parsed=None,
        text="{invalid json",
    )

    with pytest.raises(PlannerError, match="failed validation"):
        gemini_planner.create_plan("Analyze revenue", dataframe)


def test_unknown_tool_is_rejected(planner, dataframe):
    gemini_planner, client = planner

    client.models.generate_content.return_value = SimpleNamespace(
        parsed={
            "goal": "Analyze revenue",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "execute_arbitrary_python",
                    "arguments": {},
                }
            ],
        },
        text=None,
    )

    with pytest.raises(PlannerError, match="failed validation"):
        gemini_planner.create_plan("Analyze revenue", dataframe)


def test_invalid_tool_arguments_are_rejected(planner, dataframe):
    gemini_planner, client = planner

    client.models.generate_content.return_value = SimpleNamespace(
        parsed={
            "goal": "Analyze revenue",
            "steps": [
                {
                    "step_id": "step1",
                    "tool_name": "calculate_statistics",
                    "arguments": {"unknown_argument": "revenue"},
                }
            ],
        },
        text=None,
    )

    with pytest.raises(PlannerError, match="failed validation"):
        gemini_planner.create_plan("Analyze revenue", dataframe)


def test_empty_gemini_response_is_rejected(planner, dataframe):
    gemini_planner, client = planner

    client.models.generate_content.return_value = SimpleNamespace(
        parsed=None,
        text=None,
    )

    with pytest.raises(PlannerError, match="empty response"):
        gemini_planner.create_plan("Analyze revenue", dataframe)