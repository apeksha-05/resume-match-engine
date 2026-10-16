"""Talks to Supabase's admin API.

Both calls need the project's SECRET key, which can manage every user. It is
read from the server's environment only, sent only to Supabase, and never
logged or included in an error message.
"""

import uuid

import httpx

from app.core.config import get_settings

REQUEST_TIMEOUT_SECONDS = 15.0


class AuthDeletionError(Exception):
    """Raised when the login record could not be deleted. The message never contains the key."""


class UserLookupError(Exception):
    """Raised when we could not find out whether a user exists. The message never contains the key."""


def admin_api_configured() -> bool:
    settings = get_settings()
    return bool(settings.supabase_url and settings.supabase_secret_key)


def auth_deletion_configured() -> bool:
    return admin_api_configured()


def _admin_user_request(user_id: uuid.UUID) -> tuple[str, dict[str, str]]:
    settings = get_settings()
    key = settings.supabase_secret_key
    url = f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/users/{user_id}"
    # Supabase's own client libraries send the key in both headers.
    return url, {"apikey": key, "Authorization": f"Bearer {key}"}


def delete_auth_user(user_id: uuid.UUID) -> None:
    if not admin_api_configured():
        raise AuthDeletionError("SUPABASE_URL or SUPABASE_SECRET_KEY is not set.")

    url, headers = _admin_user_request(user_id)
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


def user_exists(user_id: uuid.UUID) -> bool:
    """True if the user's login still exists, False if it was deleted."""
    if not admin_api_configured():
        raise UserLookupError("SUPABASE_URL or SUPABASE_SECRET_KEY is not set.")

    url, headers = _admin_user_request(user_id)
    try:
        response = httpx.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    except httpx.HTTPError as exc:
        raise UserLookupError(f"Could not reach Supabase ({type(exc).__name__}).") from exc

    if response.status_code == 200:
        return True
    if response.status_code == 404:
        return False
    raise UserLookupError(
        f"Supabase refused the request (status {response.status_code}): {response.text[:200]}"
    )
