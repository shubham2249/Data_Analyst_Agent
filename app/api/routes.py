import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.agent.validator import PlanValidationError
from app.api.schemas import AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.tools.ingestion import DatasetIngestionError

from app.agent.gemini_planner import (
    InvalidQuestionError,
    PlannerError,
)
from app.api.schemas import (
    AnalysisResponse,
    NaturalLanguageAnalysisResponse,
)

router = APIRouter()
analysis_service = AnalysisService()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_dataset(
    file: UploadFile = File(...),
    plan: str = Form(...),
):
    try:
        raw_plan = json.loads(plan)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="The plan field must contain valid JSON.",
        ) from exc

    if not isinstance(raw_plan, dict):
        raise HTTPException(
            status_code=400,
            detail="The plan must be a JSON object.",
        )

    try:
        content = await file.read()

        result = analysis_service.execute_plan(
            filename=file.filename or "dataset.csv",
            content=content,
            raw_plan=raw_plan,
        )

        return result

    except PlanValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except DatasetIngestionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail="The analysis request is invalid.",
        ) from exc

    finally:
        await file.close()



@router.post(
    "/analyze-question",
    response_model=NaturalLanguageAnalysisResponse,
)
async def analyze_question(
    file: UploadFile = File(...),
    question: str = Form(...),
):
    try:
        content = await file.read()

        result = analysis_service.analyze_question(
            filename=file.filename or "dataset.csv",
            content=content,
            question=question,
        )

        return result

    except PlannerError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except InvalidQuestionError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except PlanValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except DatasetIngestionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()
