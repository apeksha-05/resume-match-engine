import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.analysis import Weights
from app.schemas.feedback import AnalysisFullResult


class AnalysisCreateIn(BaseModel):
    """Request body for creating a saved analysis. Provide a saved resume plus
    EITHER pasted job description text OR the id of an existing job posting."""

    resume_id: uuid.UUID
    job_description_text: str | None = Field(default=None, min_length=50, max_length=20000)
    job_id: uuid.UUID | None = None
    weights: Weights | None = None

    @field_validator("weights")
    @classmethod
    def weights_must_be_valid(cls, value: Weights | None) -> Weights | None:
        if value is None:
            return value
        values = [value.skills, value.semantic, value.experience, value.education]
        if any(v < 0 for v in values) or sum(values) <= 0:
            raise ValueError("Weights must be non-negative and must not all be zero.")
        return value

    @model_validator(mode="after")
    def require_exactly_one_target(self) -> "AnalysisCreateIn":
        has_text = self.job_description_text is not None
        has_job = self.job_id is not None
        if has_text == has_job:
            raise ValueError("Provide exactly one of job_description_text or job_id.")
        return self


class AnalysisDetailOut(AnalysisFullResult):
    """A saved analysis: the full scored result plus its identity and metadata."""

    id: uuid.UUID
    job_title: str
    company: str
    is_demo: bool
    created_at: datetime


class AnalysisHistoryItem(BaseModel):
    id: uuid.UUID
    job_title: str
    company: str
    overall_score: int
    created_at: datetime