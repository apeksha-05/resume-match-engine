import uuid

from pydantic import BaseModel, Field

from app.schemas.job import JobOut, WorkMode


class JobRecommendationOut(BaseModel):
    job: JobOut
    score: int
    matched_skills: list[str]
    missing_skills: list[str]


class RecommendationRequest(BaseModel):
    resume_id: uuid.UUID
    search: str | None = Field(default=None, max_length=100)
    work_mode: WorkMode | None = None
    max_years: int | None = Field(default=None, ge=0, le=50)
    limit: int = Field(default=10, ge=1, le=50)