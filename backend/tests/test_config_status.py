from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import config as config_router


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(config_router.router, prefix="/api/v1")
    return TestClient(app)


def test_status_reports_mock_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config_router, "get_settings", lambda: SimpleNamespace(use_mock_llm=True))

    response = make_client().get("/api/v1/config/status")

    assert response.status_code == 200
    assert response.json() == {"extraction_mode": "mock"}


def test_status_reports_ai_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config_router, "get_settings", lambda: SimpleNamespace(use_mock_llm=False))

    response = make_client().get("/api/v1/config/status")

    assert response.json() == {"extraction_mode": "ai"}


def test_status_exposes_nothing_else(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config_router, "get_settings", lambda: SimpleNamespace(use_mock_llm=True))

    response = make_client().get("/api/v1/config/status")

    assert set(response.json()) == {"extraction_mode"}


def test_default_weights_add_up_to_one():
    response = make_client().get("/api/v1/config/weights")

    assert response.status_code == 200
    assert sum(response.json().values()) == pytest.approx(1.0)
