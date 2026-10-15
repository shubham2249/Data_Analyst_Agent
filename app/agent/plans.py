from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AnalysisStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
    )
    tool_name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any] = Field(default_factory=dict)


class AnalysisPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str = Field(min_length=1, max_length=1000)
    steps: list[AnalysisStep] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def validate_unique_step_ids(self):
        step_ids = [step.step_id for step in self.steps]

        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Every step_id must be unique.")

        return self
