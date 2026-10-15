from typing import ClassVar

from pydantic import ValidationError

from app.agent.plans import AnalysisPlan, AnalysisStep
from app.tools.registry import ToolRegistry


class PlanValidationError(ValueError):
    pass


class PlanValidator:
    COLUMN_ARGUMENTS: ClassVar[dict[str, tuple[str, ...]]] = {
        "filter_data": ("column",),
        "sort_data": ("by",),
        "group_and_aggregate": ("group_by", "target_column"),
        "calculate_statistics": ("column",),
        "calculate_correlation": ("column_a", "column_b"),
        "detect_outliers": ("column",),
    }

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def validate(self, raw_plan: dict) -> AnalysisPlan:
        try:
            plan = AnalysisPlan.model_validate(raw_plan)
        except ValidationError as exc:
            raise PlanValidationError(
                "The analysis plan has an invalid structure."
            ) from exc

        for step in plan.steps:
            try:
                definition = self.registry.get(step.tool_name)
            except (KeyError, ValueError) as exc:
                raise PlanValidationError(
                    f"Unknown tool: {step.tool_name}"
                ) from exc

            try:
                definition.input_model.model_validate(step.arguments)
            except ValidationError as exc:
                raise PlanValidationError(
                    f"Invalid arguments for step '{step.step_id}'."
                ) from exc

        return plan

    def validate_step_columns(
        self,
        step: AnalysisStep,
        dataframe,
    ) -> None:
        """Validate column references against the current DataFrame schema."""
        column_arguments = self.COLUMN_ARGUMENTS.get(step.tool_name, ())
        available_columns = set(dataframe.columns)

        for argument_name in column_arguments:
            value = step.arguments.get(argument_name)

            if value is None:
                continue

            columns = value if isinstance(value, list) else [value]

            for column in columns:
                if column not in available_columns:
                    available = ", ".join(
                        repr(name) for name in dataframe.columns
                    )
                    raise PlanValidationError(
                        f"Step '{step.step_id}' ({step.tool_name}) references "
                        f"unknown column {column!r} through argument "
                        f"'{argument_name}'. Available columns: {available}."
                    )