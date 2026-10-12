from fastapi import APIRouter

from app.core.config import get_settings
from app.core.weights import DEFAULT_WEIGHTS
from app.schemas.config import StatusOut, WeightsOut

router = APIRouter()


@router.get("/config/weights", response_model=WeightsOut)
def get_default_weights() -> dict[str, float]:
    """Returns the default category weights used by the matching engine."""
    return DEFAULT_WEIGHTS


@router.get("/config/status", response_model=StatusOut)
def get_status() -> StatusOut:
    """Public. Says whether resumes are analyzed by the built-in keyword matcher
    ('mock') or by an external AI model ('ai'). Reveals nothing else."""
    mode = "mock" if get_settings().use_mock_llm else "ai"
    return StatusOut(extraction_mode=mode)