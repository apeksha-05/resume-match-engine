from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.analysis import Weights
from app.schemas.feedback import AnalysisFullResult
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume
from app.services.feedback import compute_full_analysis

router = APIRouter()


class AnalysisPreviewRequest(BaseModel):
    resume: ParsedResume
    job_description: ParsedJobDescription
    weights: Weights | None = None


@router.post("/analyses/preview", response_model=AnalysisFullResult)
def preview_analysis(payload: AnalysisPreviewRequest) -> AnalysisFullResult:
    """Computes score + suggestions + roadmap without saving anything.
    The persisted /analyses endpoint (tying together saved resume_id and
    job_id/jd_id, with history) is built in Phase 8."""
    return compute_full_analysis(payload.resume, payload.job_description, payload.weights)