from typing import Literal

from pydantic import BaseModel


class WeightsOut(BaseModel):
    skills: float
    semantic: float
    experience: float
    education: float


class StatusOut(BaseModel):
    """Tells the frontend how resumes are being analyzed, so the UI can be honest about it."""

    extraction_mode: Literal["mock", "ai"]
