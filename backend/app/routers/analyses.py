from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.analysis import AnalysisScoreResult, Weights
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume
from app.services.scoring import compute_analysis

router = APIRouter()


class AnalysisPreviewRequest(BaseModel):
    resume: ParsedResume
    job_description: ParsedJobDescription
    weights: Weights | None = None


@router.post("/analyses/preview", response_model=AnalysisScoreResult)
def preview_analysis(payload: AnalysisPreviewRequest) -> AnalysisScoreResult:
    """Computes a score without saving anything, for manually trying the
    scoring engine via /docs. The real, persisted /analyses endpoint is
    built in Phase 8."""
    return compute_analysis(payload.resume, payload.job_description, payload.weights)