
from typing import Any

import pandas as pd

from app.agent.gemini_planner import GeminiPlanner
from app.agent.plan_executor import PlanExecutor
from app.agent.results import normalize_output
from app.agent.validator import PlanValidator
from app.tools import create_tool_registry
from app.tools.ingestion import DatasetIngestion
from app.tools.profiler import DatasetProfiler


class AnalysisService:
    def __init__(self, planner=None):
        self.ingestion = DatasetIngestion()
        self.registry = create_tool_registry()
        self.plan_executor = PlanExecutor(self.registry)
        self._planner = planner
        self.profiler = DatasetProfiler()

    def inspect_dataset(
        self,
        filename: str,
        content: bytes,
    ) -> dict[str, Any]:
        dataframe = self.ingestion.load(
            filename=filename,
            content=content,
        )

        profile = self.profiler.profile(dataframe)

        return {
            "profile": profile,
            "dataframe": dataframe,
        }

    def execute_plan(
        self,
        filename: str,
        content: bytes,
        raw_plan: dict[str, Any],
    ) -> dict[str, Any]:
        dataframe = self.ingestion.load(
            filename=filename,
            content=content,
        )

        result = self.plan_executor.execute(
            raw_plan=raw_plan,
            dataframe=dataframe,
        )

        return self._serialize_result(result)

    def analyze_question(
        self,
        filename: str,
        content: bytes,
        question: str,
    ) -> dict[str, Any]:
        dataframe = self.ingestion.load(
            filename=filename,
            content=content,
        )

        if self._planner is None:
            self._planner = GeminiPlanner(
                registry=self.registry,
                validator=PlanValidator(self.registry),
            )

        plan = self._planner.create_plan(
            question=question,
            dataframe=dataframe,
        )

        result = self.plan_executor.execute(
            raw_plan=plan.model_dump(),
            dataframe=dataframe,
        )

        response = self._serialize_result(result)
        response["question"] = question
        response["plan"] = plan.model_dump()

        return response

    @staticmethod
    def _serialize_result(result) -> dict[str, Any]:
        return {
            "goal": result.goal,
            "status": result.status,
            "steps": [
                {
                    "step_id": step.step_id,
                    "tool_name": step.tool_name,
                    "status": step.status,
                    "output": step.output,
                    "error": step.error,
                }
                for step in result.steps
            ],
            "final_result": result.final_output,
            "working_dataset": normalize_output(result.final_dataframe),
        }