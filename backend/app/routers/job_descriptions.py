import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id, require_existing_user
from app.core.database import get_db
from app.core.limits import limit_job_descriptions
from app.models.job_description import JobDescription
from app.schemas.job_description import JobDescriptionIn, JobDescriptionOut
from app.services.jd_extraction import JdExtractionError, extract_structured_jd

router = APIRouter()


@router.post(
    "/job-descriptions",
    response_model=JobDescriptionOut,
    status_code=201,
    dependencies=[Depends(limit_job_descriptions), Depends(require_existing_user)],
)
def submit_job_description(
    payload: JobDescriptionIn,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> JobDescriptionOut:
    try:
        parsed = extract_structured_jd(payload.text)
    except JdExtractionError as exc:
        raise HTTPException(
            status_code=503, detail="Job description analysis is currently unavailable."
        ) from exc

    jd = JobDescription(
        user_id=user_id,
        title=parsed.title,
        parsed=parsed.model_dump(mode="json"),
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return JobDescriptionOut.model_validate(
        {"id": jd.id, "title": jd.title, "parsed": parsed, "created_at": jd.created_at}
    )


@router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionOut)
def get_job_description(
    jd_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> JobDescriptionOut:
    jd = db.get(JobDescription, jd_id)
    if jd is None or jd.user_id != user_id:
        raise HTTPException(status_code=404, detail="Job description not found")

    return JobDescriptionOut.model_validate(
        {"id": jd.id, "title": jd.title, "parsed": jd.parsed, "created_at": jd.created_at}
    )
