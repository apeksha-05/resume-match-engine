import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.job import Job
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.analysis import Weights
from app.schemas.analysis_records import (
    AnalysisCreateIn,
    AnalysisDetailOut,
    AnalysisHistoryItem,
)
from app.schemas.feedback import AnalysisFullResult
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume
from app.services.analysis_records import (
    pack_analysis,
    short_title,
    to_history_item,
    unpack_analysis,
)
from app.services.feedback import compute_full_analysis
from app.services.jd_extraction import JdExtractionError, extract_structured_jd
from app.services.recommendation import job_to_parsed_jd

router = APIRouter()


class AnalysisPreviewRequest(BaseModel):
    resume: ParsedResume
    job_description: ParsedJobDescription
    weights: Weights | None = None


@router.post("/analyses/preview", response_model=AnalysisFullResult)
def preview_analysis(payload: AnalysisPreviewRequest) -> AnalysisFullResult:
    """Computes score + suggestions + roadmap without saving anything.
    A developer tool for trying the scoring engine from /docs."""
    return compute_full_analysis(payload.resume, payload.job_description, payload.weights)


@router.post("/analyses", response_model=AnalysisDetailOut, status_code=201)
def create_analysis(
    payload: AnalysisCreateIn,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AnalysisDetailOut:
    resume = db.get(Resume, payload.resume_id)
    if resume is None or resume.user_id != user_id:
        raise HTTPException(status_code=404, detail="Resume not found")
    parsed_resume = ParsedResume.model_validate(resume.parsed)

    jd_id: uuid.UUID | None = None
    job_id: uuid.UUID | None = None

    if payload.job_id is not None:
        job = db.get(Job, payload.job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        parsed_jd = job_to_parsed_jd(job)
        job_title, company, is_demo = job.title, job.company, job.is_demo
        job_id = job.id
    else:
        try:
            parsed_jd = extract_structured_jd(payload.job_description_text or "")
        except JdExtractionError as exc:
            raise HTTPException(
                status_code=503, detail="Job description analysis is currently unavailable."
            ) from exc
        job_title = short_title(parsed_jd.title)
        company = "Pasted job description"
        is_demo = False
        jd_row = JobDescription(
            user_id=user_id,
            title=job_title,
            parsed=parsed_jd.model_dump(mode="json"),
        )
        db.add(jd_row)
        db.flush()  # assigns jd_row.id before we reference it below
        jd_id = jd_row.id

    full = compute_full_analysis(parsed_resume, parsed_jd, payload.weights)

    row = Analysis(
        user_id=user_id,
        resume_id=resume.id,
        jd_id=jd_id,
        job_id=job_id,
        **pack_analysis(full, job_title, company, is_demo),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return unpack_analysis(row)


@router.get("/analyses", response_model=list[AnalysisHistoryItem])
def list_analyses(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[AnalysisHistoryItem]:
    stmt = (
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).scalars().all()
    return [to_history_item(row) for row in rows]


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetailOut)
def get_analysis(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AnalysisDetailOut:
    row = db.get(Analysis, analysis_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return unpack_analysis(row)


@router.delete("/analyses/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    row = db.get(Analysis, analysis_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(row)
    db.commit()