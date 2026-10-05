import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dev_auth import get_current_user_id
from app.models.resume import Resume
from app.schemas.recommendation import JobRecommendationOut, RecommendationRequest
from app.schemas.resume import ParsedResume
from app.services.recommendation import recommend_jobs

router = APIRouter()


@router.post("/recommendations", response_model=list[JobRecommendationOut])
def get_recommendations(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[JobRecommendationOut]:
    resume = db.get(Resume, payload.resume_id)
    if resume is None or resume.user_id != user_id:
        raise HTTPException(status_code=404, detail="Resume not found")

    parsed_resume = ParsedResume.model_validate(resume.parsed)

    return recommend_jobs(
        db=db,
        resume=parsed_resume,
        work_mode=payload.work_mode,
        max_years=payload.max_years,
        limit=payload.limit,
    )