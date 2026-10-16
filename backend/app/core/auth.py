"""Real Supabase JWT verification using the project's JWKS endpoint."""

import logging
import uuid
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings
from app.services.supabase_admin import UserLookupError, admin_api_configured, user_exists

settings = get_settings()
_security = HTTPBearer()

# Uses uvicorn's own logger so messages always show in the server terminal.
logger = logging.getLogger("uvicorn.error")

CLOCK_SKEW_SECONDS = 10
INVALID_TOKEN_MESSAGE = "Invalid or expired authentication token"


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> uuid.UUID:
    """Verifies the bearer token's signature against Supabase's public keys and
    returns the authenticated user's id (the token's 'sub' claim).

    Only ES256 is accepted, and the token must carry an expiry, a subject and
    the 'authenticated' audience. The detailed reason for a rejection is
    logged on the server only, and never includes the token itself.
    """
    if not settings.supabase_url:
        logger.error("SUPABASE_URL is not set in backend/.env, so tokens cannot be verified.")
        raise HTTPException(
            status_code=500, detail="Authentication is not configured on the server."
        )

    token = credentials.credentials

    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            leeway=CLOCK_SKEW_SECONDS,
            options={"require": ["exp", "sub", "aud"]},
        )
    except jwt.exceptions.PyJWKClientConnectionError as exc:
        # The keys could not be downloaded. That is our problem, not a bad login.
        logger.warning("Could not fetch Supabase signing keys: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="The sign-in service is temporarily unavailable. Please try again.",
        ) from exc
    except jwt.PyJWTError as exc:
        logger.warning("JWT verification failed: %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=401, detail=INVALID_TOKEN_MESSAGE) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(status_code=401, detail=INVALID_TOKEN_MESSAGE)
    try:
        return uuid.UUID(subject)
    except ValueError as exc:
        logger.warning("JWT subject is not a valid user id.")
        raise HTTPException(status_code=401, detail=INVALID_TOKEN_MESSAGE) from exc


def require_existing_user(user_id: uuid.UUID = Depends(get_current_user_id)) -> None:
    """Rejects tokens that belong to a deleted account.

    A login token stays validly signed until it expires, even after the
    account is deleted. Without this check, a leftover token could upload a
    new resume and create data that nobody can delete. It costs one call to
    Supabase, so it is used only on endpoints that create new data.
    """
    if not admin_api_configured():
        if settings.environment == "production":
            logger.error("SUPABASE_SECRET_KEY is not set, so account existence cannot be checked.")
            raise HTTPException(
                status_code=503,
                detail="Account verification is not configured on the server.",
            )
        return  # In development, skip the check rather than block local work.

    try:
        exists = user_exists(user_id)
    except UserLookupError as exc:
        logger.warning("User lookup failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Could not verify your account right now. Please try again.",
        ) from exc

    if not exists:
        raise HTTPException(
            status_code=401,
            detail="This account no longer exists. Please sign up again.",
        )
