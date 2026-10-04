import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ParsedJobDescription(BaseModel):
    """Structured job description data, extracted and validated from pasted text."""

    title: str = Field(description="The job title, as stated or best inferred from the text")
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    min_years_experience: int | None = None
    education_requirement: str | None = None


class JobDescriptionIn(BaseModel):
    text: str = Field(min_length=50, description="The full pasted job description text")


class JobDescriptionOut(BaseModel):
    id: uuid.UUID
    title: str
    parsed: ParsedJobDescription
    created_at: datetime