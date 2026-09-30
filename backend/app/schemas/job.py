import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

WorkMode = Literal["remote", "hybrid", "onsite"]


class JobOut(BaseModel):
    """What the API returns for a single job posting."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str
    description: str
    location: str
    work_mode: WorkMode
    min_years: int
    required_skills: list[str]
    preferred_skills: list[str]
    is_demo: bool
    created_at: datetime


class JobListOut(BaseModel):
    """Paginated list response for GET /jobs."""

    items: list[JobOut]
    total: int