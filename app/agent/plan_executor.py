import logging
from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd

from app.agent.executor import ToolExecutionError, ToolExecutor
from app.agent.results import normalize_output
from app.agent.validator import PlanValidationError, PlanValidator
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

@dataclass
class StepExecutionResult:
    step_id: str
    tool_name: str
    status: Literal["completed", "failed"]
    output: Any = None
    error: str | None = None


@dataclass
class PlanExecutionResult:
    goal: str
    status: Literal["completed", "failed"]
    steps: list[StepExecutionResult]
    final_dataframe: pd.DataFrame
    final_output: Any = None


class PlanExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.validator = PlanValidator(registry)
        self.tool_executor = ToolExecutor(registry)

    def execute(
        self,
        raw_plan: dict,
        dataframe: pd.DataFrame,
    ) -> PlanExecutionResult:
        plan = self.validator.validate(raw_plan)

        current_df = dataframe.copy()
        step_results: list[StepExecutionResult] = []
        final_output = None

        
        for step in plan.steps:
            try:
                self.validator.validate_step_columns(
                    step=step,
                    dataframe=current_df,
                )

                output = self.tool_executor.execute(
                    tool_name=step.tool_name,
                    arguments=step.arguments,
                    context={"df": current_df},
                )

            except PlanValidationError as exc:
                step_results.append(
                    StepExecutionResult(
                        step_id=step.step_id,
                        tool_name=step.tool_name,
                        status="failed",
                        error=str(exc),
                    )
                )

                return PlanExecutionResult(
                    goal=plan.goal,
                    status="failed",
                    steps=step_results,
                    final_dataframe=current_df,
                    final_output=final_output,
                )

            except ToolExecutionError as exc:
                logger.exception(
                    "Tool execution failed at step '%s' (%s).",
                    step.step_id,
                    step.tool_name,
                )

                step_results.append(
                    StepExecutionResult(
                        step_id=step.step_id,
                        tool_name=step.tool_name,
                        status="failed",
                        error=str(exc),
                    )
                )

                return PlanExecutionResult(
                    goal=plan.goal,
                    status="failed",
                    steps=step_results,
                    final_dataframe=current_df,
                    final_output=final_output,
                )

            if isinstance(output, pd.DataFrame):
                current_df = output

            final_output = normalize_output(output)

            step_results.append(
                StepExecutionResult(
                    step_id=step.step_id,
                    tool_name=step.tool_name,
                    status="completed",
                    output=final_output,
                )
            )
        
        return PlanExecutionResult(
            goal=plan.goal,
            status="completed",
            steps=step_results,
            final_dataframe=current_df,
            final_output=final_output,
        )