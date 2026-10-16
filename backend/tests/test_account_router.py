import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.routers import account as account_router
from app.services.supabase_admin import AuthDeletionError

USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def make_client(authenticated: bool = True) -> tuple[TestClient, MagicMock]:
    fake_db = MagicMock()
    app = FastAPI()
    app.include_router(account_router.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: fake_db
    if authenticated:
        app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    return TestClient(app), fake_db


def test_summary_returns_counts():
    client, fake_db = make_client()
    fake_db.execute.return_value.scalar_one.side_effect = [2, 5, 1]

    response = client.get("/api/v1/account/summary")

    assert response.status_code == 200
    assert response.json() == {"resumes": 2, "analyses": 5, "job_descriptions": 1}


def test_delete_data_keeps_the_login(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    monkeypatch.setattr(
        account_router, "delete_user_data", lambda db, user_id: calls.append("data")
    )
    monkeypatch.setattr(account_router, "delete_auth_user", lambda user_id: calls.append("login"))
    client, _ = make_client()

    response = client.delete("/api/v1/account/data")

    assert response.status_code == 204
    assert calls == ["data"]


def test_delete_account_removes_data_before_login(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    monkeypatch.setattr(account_router, "auth_deletion_configured", lambda: True)
    monkeypatch.setattr(
        account_router, "delete_user_data", lambda db, user_id: calls.append("data")
    )
    monkeypatch.setattr(account_router, "delete_auth_user", lambda user_id: calls.append("login"))
    client, _ = make_client()

    response = client.delete("/api/v1/account")

    assert response.status_code == 204
    assert calls == ["data", "login"]


def test_delete_account_deletes_nothing_when_not_configured(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    monkeypatch.setattr(account_router, "auth_deletion_configured", lambda: False)
    monkeypatch.setattr(
        account_router, "delete_user_data", lambda db, user_id: calls.append("data")
    )
    monkeypatch.setattr(account_router, "delete_auth_user", lambda user_id: calls.append("login"))
    client, _ = make_client()

    response = client.delete("/api/v1/account")

    assert response.status_code == 503
    assert calls == []


def test_delete_account_reports_a_login_failure_after_data_is_gone(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []

    def failing_login(user_id: uuid.UUID) -> None:
        raise AuthDeletionError("Supabase refused the request (status 401)")

    monkeypatch.setattr(account_router, "auth_deletion_configured", lambda: True)
    monkeypatch.setattr(
        account_router, "delete_user_data", lambda db, user_id: calls.append("data")
    )
    monkeypatch.setattr(account_router, "delete_auth_user", failing_login)
    client, _ = make_client()

    response = client.delete("/api/v1/account")

    assert response.status_code == 502
    assert "data was deleted" in response.json()["detail"]
    assert calls == ["data"]


def test_account_endpoints_require_login(monkeypatch: pytest.MonkeyPatch):
    def must_not_run(*args, **kwargs):
        raise AssertionError("Nothing should run without a login.")

    monkeypatch.setattr(account_router, "delete_user_data", must_not_run)
    monkeypatch.setattr(account_router, "delete_auth_user", must_not_run)
    monkeypatch.setattr(account_router, "get_account_summary", must_not_run)
    client, _ = make_client(authenticated=False)

    for method, path in [
        ("GET", "/api/v1/account/summary"),
        ("DELETE", "/api/v1/account/data"),
        ("DELETE", "/api/v1/account"),
    ]:
        assert client.request(method, path).status_code in (401, 403)
