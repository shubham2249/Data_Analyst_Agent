from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StepResultResponse(APIModel):
    step_id: str
    tool_name: str
    status: Literal["completed", "failed"]
    output: dict[str, Any] | None = None
    error: str | None = None


class DatasetPreviewResponse(APIModel):
    output_type: str
    data: list[dict[str, Any]]
    metadata: dict[str, Any]


class AnalysisResponse(APIModel):
    goal: str
    status: Literal["completed", "failed"]
    steps: list[StepResultResponse]
    final_result: dict[str, Any] | None = None
    working_dataset: DatasetPreviewResponse


class DatasetInspectionResponse(APIModel):
    profile: dict[str, Any]
    preview: DatasetPreviewResponse


class APIErrorResponse(APIModel):
    detail: str


class HealthResponse(APIModel):
    status: Literal["ok"]
    service: str = "InsightIQ"


class AnalysisRequest(APIModel):
    goal: str = Field(min_length=1, max_length=1000)
    steps: list[dict[str, Any]] = Field(min_length=1, max_length=10)



class NaturalLanguageAnalysisResponse(AnalysisResponse):
    question: str
    plan: dict[str, Any]