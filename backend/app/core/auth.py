"""Real Supabase JWT verification using the project's JWKS endpoint.
Replaces the old development-only placeholder user.
"""

import logging
import uuid
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings

settings = get_settings()
_security = HTTPBearer()

# Uses uvicorn's own logger so messages always show in the server terminal.
logger = logging.getLogger("uvicorn.error")


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> uuid.UUID:
    """FastAPI dependency: verifies the bearer token's signature against
    Supabase's public JWKS and returns the authenticated user's ID (the
    token's 'sub' claim). Raises 401 if the token is missing, expired, or
    invalid. The detailed reason is logged on the server only."""
    if not settings.supabase_url:
        logger.error("SUPABASE_URL is not set in backend/.env, so tokens cannot be verified.")
        raise HTTPException(status_code=500, detail="Authentication is not configured on the server.")

    token = credentials.credentials

    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        # Log the error type and message only. Never log the token itself.
        logger.warning("JWT verification failed: %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token") from exc

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token is missing a user identifier")

    return uuid.UUID(user_id_str)