import uuid
from types import SimpleNamespace

import httpx
import pytest

from app.services import supabase_admin
from app.services.supabase_admin import (
    AuthDeletionError,
    UserLookupError,
    auth_deletion_configured,
    delete_auth_user,
    user_exists,
)

SECRET = "sb_secret_test_value_123"
BASE_URL = "https://example-ref.supabase.co"
USER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


def configure(monkeypatch: pytest.MonkeyPatch, url: str = BASE_URL, key: str = SECRET) -> None:
    monkeypatch.setattr(
        supabase_admin,
        "get_settings",
        lambda: SimpleNamespace(supabase_url=url, supabase_secret_key=key),
    )


def fake_response(status: int, body: str = "") -> httpx.Response:
    return httpx.Response(status, text=body, request=httpx.Request("DELETE", BASE_URL))


def test_not_configured_without_a_secret_key(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch, key="")

    assert auth_deletion_configured() is False


def test_configured_when_url_and_key_are_set(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)

    assert auth_deletion_configured() is True


def test_delete_sends_the_expected_request(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)
    captured: dict = {}

    def fake_delete(url, headers, timeout):
        captured.update(url=url, headers=headers)
        return fake_response(200)

    monkeypatch.setattr(supabase_admin.httpx, "delete", fake_delete)

    delete_auth_user(USER_ID)

    assert captured["url"] == f"{BASE_URL}/auth/v1/admin/users/{USER_ID}"
    assert captured["headers"]["apikey"] == SECRET
    assert captured["headers"]["Authorization"] == f"Bearer {SECRET}"


def test_missing_user_counts_as_success(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)
    monkeypatch.setattr(
        supabase_admin.httpx, "delete", lambda url, headers, timeout: fake_response(404)
    )

    delete_auth_user(USER_ID)  # must not raise


def test_refusal_raises_without_leaking_the_key(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)
    monkeypatch.setattr(
        supabase_admin.httpx, "delete", lambda url, headers, timeout: fake_response(401, "unauthorized")
    )

    with pytest.raises(AuthDeletionError) as error:
        delete_auth_user(USER_ID)

    assert "401" in str(error.value)
    assert SECRET not in str(error.value)


def test_network_failure_raises(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)

    def boom(url, headers, timeout):
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(supabase_admin.httpx, "delete", boom)

    with pytest.raises(AuthDeletionError):
        delete_auth_user(USER_ID)


def test_delete_raises_when_not_configured(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch, key="")

    def must_not_be_called(url, headers, timeout):
        raise AssertionError("No request should be sent without a key.")

    monkeypatch.setattr(supabase_admin.httpx, "delete", must_not_be_called)

    with pytest.raises(AuthDeletionError):
        delete_auth_user(USER_ID)
        
def test_user_exists_returns_true_for_a_200(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)
    captured: dict = {}

    def fake_get(url, headers, timeout):
        captured.update(url=url, headers=headers)
        return fake_response(200, "{}")

    monkeypatch.setattr(supabase_admin.httpx, "get", fake_get)

    assert user_exists(USER_ID) is True
    assert captured["url"] == f"{BASE_URL}/auth/v1/admin/users/{USER_ID}"
    assert captured["headers"]["apikey"] == SECRET


def test_user_exists_returns_false_for_a_404(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)
    monkeypatch.setattr(
        supabase_admin.httpx, "get", lambda url, headers, timeout: fake_response(404)
    )

    assert user_exists(USER_ID) is False


def test_user_exists_raises_for_other_statuses_without_leaking_the_key(
    monkeypatch: pytest.MonkeyPatch,
):
    configure(monkeypatch)
    monkeypatch.setattr(
        supabase_admin.httpx, "get", lambda url, headers, timeout: fake_response(500, "oops")
    )

    with pytest.raises(UserLookupError) as error:
        user_exists(USER_ID)

    assert "500" in str(error.value)
    assert SECRET not in str(error.value)


def test_user_exists_raises_on_network_failure(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch)

    def boom(url, headers, timeout):
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(supabase_admin.httpx, "get", boom)

    with pytest.raises(UserLookupError):
        user_exists(USER_ID)


def test_user_exists_raises_when_not_configured(monkeypatch: pytest.MonkeyPatch):
    configure(monkeypatch, key="")

    def must_not_be_called(url, headers, timeout):
        raise AssertionError("No request should be sent without a key.")

    monkeypatch.setattr(supabase_admin.httpx, "get", must_not_be_called)

    with pytest.raises(UserLookupError):
        user_exists(USER_ID)