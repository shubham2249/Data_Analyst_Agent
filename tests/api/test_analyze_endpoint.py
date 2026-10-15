import io
import json

from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import Mock
from app.api.routes import analysis_service


client = TestClient(app)


def test_analyze_endpoint():
    csv_content = b"region,revenue\nNorth,100\nNorth,150\nSouth,200\n"

    plan = {
        "goal": "Calculate average revenue by region",
        "steps": [
            {
                "step_id": "average_revenue",
                "tool_name": "group_and_aggregate",
                "arguments": {
                    "group_by": "region",
                    "target_column": "revenue",
                    "aggregation": "mean",
                },
            }
        ],
    }

    response = client.post(
        "/api/analyze",
        files={
            "file": (
                "sales.csv",
                io.BytesIO(csv_content),
                "text/csv",
            )
        },
        data={"plan": json.dumps(plan)},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["steps"][0]["status"] == "completed"

    aggregated_rows = body["steps"][0]["output"]["data"]

    averages = {
        row["region"]: row["mean_revenue"]
        for row in aggregated_rows
    }

    assert averages == {"North": 125.0, "South": 200.0}


def test_analyze_question_endpoint(monkeypatch):
    csv_content = b"region,revenue\nNorth,100\nNorth,150\nSouth,200\n"

    fake_plan = {
        "goal": "Calculate average revenue by region",
        "steps": [
            {
                "step_id": "average_revenue",
                "tool_name": "group_and_aggregate",
                "arguments": {
                    "group_by": "region",
                    "target_column": "revenue",
                    "aggregation": "mean",
                },
            }
        ],
    }

    mock_planner = Mock()
    mock_planner.create_plan.return_value = (
        __import__("app.agent.plans", fromlist=["AnalysisPlan"])
        .AnalysisPlan.model_validate(fake_plan)
    )

    monkeypatch.setattr(
        analysis_service,
        "_planner",
        mock_planner,
    )

    response = client.post(
        "/api/analyze-question",
        files={
            "file": (
                "sales.csv",
                io.BytesIO(csv_content),
                "text/csv",
            )
        },
        data={
            "question": "Calculate average revenue by region"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["question"] == "Calculate average revenue by region"
    assert body["status"] == "completed"
    assert body["plan"]["goal"] == "Calculate average revenue by region"

    rows = body["final_result"]["data"]
    averages = {row["region"]: row["mean_revenue"] for row in rows}

    assert averages == {"North": 125.0, "South": 200.0}
    mock_planner.create_plan.assert_called_once()


def test_analyze_question_rejects_empty_question():
    response = client.post(
        "/api/analyze-question",
        files={
            "file": (
                "sales.csv",
                io.BytesIO(b"region,revenue\nNorth,100\n"),
                "text/csv",
            )
        },
        data={"question": "   "},
    )

    assert response.status_code == 502
    assert "analysis question" in response.json()["detail"]