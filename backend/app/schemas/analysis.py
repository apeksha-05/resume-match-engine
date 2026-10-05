from typing import Literal

from pydantic import BaseModel

CategoryKey = Literal["skills", "semantic", "experience", "education"]


class Weights(BaseModel):
    skills: float
    semantic: float
    experience: float
    education: float


class CategoryScore(BaseModel):
    key: CategoryKey
    label: str
    score: float  # 0 to 1
    weight: float  # the weight actually used, after N/A redistribution
    applicable: bool
    explanation: str


class SkillMatch(BaseModel):
    name: str
    evidence: str


class EvidenceItem(BaseModel):
    requirement: str
    snippet: str
    similarity: float


class AnalysisScoreResult(BaseModel):
    overall_score: int  # 0 to 100
    weights: Weights
    categories: list[CategoryScore]
    matched_required: list[SkillMatch]
    missing_required: list[str]
    matched_preferred: list[SkillMatch]
    missing_preferred: list[str]
    evidence: list[EvidenceItem]
    calculation_notes: list[str]