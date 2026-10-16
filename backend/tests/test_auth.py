import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import auth
from app.services.supabase_admin import UserLookupError

USER_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")
SIGNING_KEY = ec.generate_private_key(ec.SECP256R1())
ATTACKER_KEY = ec.generate_private_key(ec.SECP256R1())
LONG_HMAC_SECRET = "an-hmac-secret-that-is-long-enough-to-avoid-warnings"


class FakeJwksClient:
    """Stands in for the real key client, so no network call is made."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
        if self.error is not None:
            raise self.error
        return SimpleNamespace(key=SIGNING_KEY.public_key())


@pytest.fixture(autouse=True)
def use_fake_jwks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth, "_get_jwks_client", lambda: FakeJwksClient())


def make_token(
    *,
    key=SIGNING_KEY,
    algorithm: str = "ES256",
    subject: str | None = str(USER_ID),
    audience: str = "authenticated",
    expires_in: int | None = 3600,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {"aud": audience, "iat": now}
    if subject is not None:
        payload["sub"] = subject
    if expires_in is not None:
        payload["exp"] = now + timedelta(seconds=expires_in)
    return jwt.encode(payload, key, algorithm=algorithm, headers={"kid": "test-key"})


def verify(token: str) -> uuid.UUID:
    return auth.get_current_user_id(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    )


def assert_rejected(token: str, status: int = 401) -> None:
    with pytest.raises(HTTPException) as error:
        verify(token)
    assert error.value.status_code == status


def test_accepts_a_valid_token():
    assert verify(make_token()) == USER_ID


def test_rejects_an_expired_token():
    assert_rejected(make_token(expires_in=-3600))


def test_allows_a_few_seconds_of_clock_skew():
    assert verify(make_token(expires_in=-5)) == USER_ID


def test_rejects_the_wrong_audience():
    assert_rejected(make_token(audience="anon"))


def test_rejects_a_token_signed_with_another_key():
    assert_rejected(make_token(key=ATTACKER_KEY))


def test_rejects_hmac_signed_tokens():
    assert_rejected(make_token(key=LONG_HMAC_SECRET, algorithm="HS256"))


def test_rejects_unsigned_tokens():
    assert_rejected(make_token(key=None, algorithm="none"))


def test_rejects_a_token_without_an_expiry():
    assert_rejected(make_token(expires_in=None))


def test_rejects_a_token_without_a_subject():
    assert_rejected(make_token(subject=None))


def test_rejects_a_subject_that_is_not_a_user_id():
    assert_rejected(make_token(subject="not-a-uuid"))


def test_rejects_garbage():
    assert_rejected("this-is-not-a-token")


def test_reports_503_when_the_key_service_is_unreachable(monkeypatch: pytest.MonkeyPatch):
    error = jwt.exceptions.PyJWKClientConnectionError("down")
    monkeypatch.setattr(auth, "_get_jwks_client", lambda: FakeJwksClient(error))

    assert_rejected(make_token(), status=503)


def test_reports_500_when_the_server_is_not_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        auth, "settings", SimpleNamespace(supabase_url="", environment="development")
    )

    assert_rejected(make_token(), status=500)


def setup_existence_check(
    monkeypatch: pytest.MonkeyPatch,
    *,
    environment: str = "development",
    configured: bool = True,
    exists: bool = True,
    lookup_error: Exception | None = None,
) -> None:
    monkeypatch.setattr(
        auth,
        "settings",
        SimpleNamespace(supabase_url="https://x.supabase.co", environment=environment),
    )
    monkeypatch.setattr(auth, "admin_api_configured", lambda: configured)

    def fake_user_exists(user_id: uuid.UUID) -> bool:
        if lookup_error is not None:
            raise lookup_error
        return exists

    monkeypatch.setattr(auth, "user_exists", fake_user_exists)


def test_an_existing_user_passes_the_existence_check(monkeypatch: pytest.MonkeyPatch):
    setup_existence_check(monkeypatch, exists=True)

    auth.require_existing_user(user_id=USER_ID)  # must not raise


def test_a_deleted_user_is_rejected(monkeypatch: pytest.MonkeyPatch):
    setup_existence_check(monkeypatch, exists=False)

    with pytest.raises(HTTPException) as error:
        auth.require_existing_user(user_id=USER_ID)

    assert error.value.status_code == 401
    assert "no longer exists" in error.value.detail


def test_a_failed_lookup_returns_503(monkeypatch: pytest.MonkeyPatch):
    setup_existence_check(monkeypatch, lookup_error=UserLookupError("down"))

    with pytest.raises(HTTPException) as error:
        auth.require_existing_user(user_id=USER_ID)

    assert error.value.status_code == 503


def test_the_check_is_skipped_in_development_without_a_key(monkeypatch: pytest.MonkeyPatch):
    setup_existence_check(monkeypatch, configured=False)

    def must_not_run(user_id: uuid.UUID) -> bool:
        raise AssertionError("No lookup should happen without a key.")

    monkeypatch.setattr(auth, "user_exists", must_not_run)

    auth.require_existing_user(user_id=USER_ID)  # must not raise


def test_the_check_fails_closed_in_production_without_a_key(monkeypatch: pytest.MonkeyPatch):
    setup_existence_check(monkeypatch, environment="production", configured=False)

    with pytest.raises(HTTPException) as error:
        auth.require_existing_user(user_id=USER_ID)

    assert error.value.status_code == 503
