from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple liveness check. Used by Render's health monitor in Phase 11."""
    return {"status": "ok"}