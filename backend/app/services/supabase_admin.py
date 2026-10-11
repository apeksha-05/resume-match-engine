"""Deletes a user's login record through Supabase's admin API.

This needs the project's SECRET key, which can manage every user. It is read
from the server's environment only, sent only to Supabase, and never logged or
included in an error message.
"""

import logging
import uuid

import httpx

from app.core.config import get_settings

logger = logging.getLogger("uvicorn.error")

REQUEST_TIMEOUT_SECONDS = 15.0


class AuthDeletionError(Exception):
    """Raised when the login record could not be deleted. The message never contains the key."""


def auth_deletion_configured() -> bool:
    settings = get_settings()
    return bool(settings.supabase_url and settings.supabase_secret_key)


def delete_auth_user(user_id: uuid.UUID) -> None:
    settings = get_settings()
    if not (settings.supabase_url and settings.supabase_secret_key):
        raise AuthDeletionError("SUPABASE_URL or SUPABASE_SECRET_KEY is not set.")

    url = f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/users/{user_id}"
    key = settings.supabase_secret_key
    # Supabase's own client libraries send the key in both headers.
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}

    try:
        response = httpx.delete(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    except httpx.HTTPError as exc:
        raise AuthDeletionError(f"Could not reach Supabase ({type(exc).__name__}).") from exc

    if response.status_code == 404:
        return  # The login is already gone, so a retry counts as success.
    if response.status_code >= 400:
        raise AuthDeletionError(
            f"Supabase refused the request (status {response.status_code}): {response.text[:200]}"
        )