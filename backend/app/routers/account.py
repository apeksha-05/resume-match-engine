import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.limits import limit_account_changes
from app.schemas.account import AccountSummaryOut
from app.services.account import delete_user_data, get_account_summary
from app.services.supabase_admin import (
    AuthDeletionError,
    auth_deletion_configured,
    delete_auth_user,
)

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


@router.get("/account/summary", response_model=AccountSummaryOut)
def account_summary(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AccountSummaryOut:
    return get_account_summary(db, user_id)


@router.delete("/account/data", status_code=204, dependencies=[Depends(limit_account_changes)])
def delete_my_data(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    """Deletes all of the user's saved data but keeps their login."""
    delete_user_data(db, user_id)


@router.delete("/account", status_code=204, dependencies=[Depends(limit_account_changes)])
def delete_my_account(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    """Deletes all of the user's saved data, then their login."""
    # Check first, so a missing key can never leave an account half-deleted.
    if not auth_deletion_configured():
        raise HTTPException(
            status_code=503,
            detail="Account deletion is not available on this server. Nothing was deleted.",
        )

    delete_user_data(db, user_id)

    try:
        delete_auth_user(user_id)
    except AuthDeletionError as exc:
        logger.warning("Login deletion failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Your saved data was deleted, but removing your login failed. Please try again.",
        ) from exc