from fastapi import APIRouter

from app.core.weights import DEFAULT_WEIGHTS
from app.schemas.config import WeightsOut

router = APIRouter()


@router.get("/config/weights", response_model=WeightsOut)
def get_default_weights() -> dict[str, float]:
    """Returns the default category weights used by the matching engine."""
    return DEFAULT_WEIGHTS