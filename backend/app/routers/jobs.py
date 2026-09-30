import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job
from app.schemas.job import JobListOut, JobOut, WorkMode

router = APIRouter()


@router.get("/jobs", response_model=JobListOut)
def list_jobs(
    db: Session = Depends(get_db),
    search: str | None = Query(default=None, description="Matches title, company, or location"),
    work_mode: WorkMode | None = Query(default=None),
    max_years: int | None = Query(default=None, ge=0, description="Only jobs requiring at most this many years"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> JobListOut:
    stmt = select(Job)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Job.title.ilike(pattern),
                Job.company.ilike(pattern),
                Job.location.ilike(pattern),
            )
        )
    if work_mode:
        stmt = stmt.where(Job.work_mode == work_mode)
    if max_years is not None:
        stmt = stmt.where(Job.min_years <= max_years)

    total = len(db.execute(stmt).all())

    stmt = stmt.order_by(Job.created_at.desc()).offset(offset).limit(limit)
    jobs = db.execute(stmt).scalars().all()

    return JobListOut(items=[JobOut.model_validate(job) for job in jobs], total=total)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> JobOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut.model_validate(job)