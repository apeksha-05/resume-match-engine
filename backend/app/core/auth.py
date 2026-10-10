"""Real Supabase JWT verification using the project's JWKS endpoint.
Replaces app/core/dev_auth.py's hardcoded placeholder user.
"""

import uuid
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings

settings = get_settings()
_security = HTTPBearer()


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> uuid.UUID:
    """FastAPI dependency: verifies the bearer token's signature against
    Supabase's public JWKS and returns the authenticated user's ID (the
    token's 'sub' claim). Raises 401 if the token is missing, expired, or
    invalid."""
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
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token") from exc

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token is missing a user identifier")

    return uuid.UUID(user_id_str)