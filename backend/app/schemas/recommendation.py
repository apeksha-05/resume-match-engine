import uuid

from pydantic import BaseModel

from app.schemas.job import JobOut


class JobRecommendationOut(BaseModel):
    job: JobOut
    score: int
    matched_skills: list[str]
    missing_skills: list[str]


class RecommendationRequest(BaseModel):
    resume_id: uuid.UUID
    work_mode: str | None = None
    max_years: int | None = None
    limit: int = 10