from pydantic import BaseModel

from app.schemas.analysis import AnalysisScoreResult


class BulletSuggestion(BaseModel):
    original: str
    suggested: str
    why_changed: str


class RoadmapItem(BaseModel):
    skill: str
    reason: str
    steps: list[str]
    estimated_weeks: int


class AnalysisFullResult(AnalysisScoreResult):
    """Extends the deterministic score with AI-generated (or mock) feedback.
    Matches the shape the frontend's AnalysisResult type already expects."""

    suggestions: list[BulletSuggestion]
    roadmap: list[RoadmapItem]