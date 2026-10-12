import logging

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.rate_limit import SlidingWindowLimiter
from app.core.security_middleware import (
    GENERIC_ERROR_MESSAGE,
    install_security_middleware,
    summarize_exception,
)

SECRET_TEXT = "my private resume text 12345"


def make_client(**overrides) -> TestClient:
    options = {
        "max_request_bytes": 1000,
        "ip_limiter": None,
        "production": False,
        "log_tracebacks": False,
    }
    options.update(overrides)

    app = FastAPI()
    install_security_middleware(app, **options)

    @app.get("/ok")
    def ok() -> dict[str, str]:
        return {"status": "fine"}

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/boom")
    def boom() -> dict[str, str]:
        raise ValueError(SECRET_TEXT)

    @app.post("/echo")
    async def echo(request: Request) -> dict[str, int]:
        return {"size": len(await request.body())}

    return TestClient(app)


def test_adds_security_headers():
    response = make_client().get("/ok")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"


def test_adds_hsts_only_in_production():
    assert "Strict-Transport-Security" not in make_client().get("/ok").headers
    assert "Strict-Transport-Security" in make_client(production=True).get("/ok").headers


def test_unexpected_errors_return_a_generic_500():
    response = make_client().get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": GENERIC_ERROR_MESSAGE}
    assert SECRET_TEXT not in response.text


def test_unexpected_errors_are_logged_without_their_message(caplog):
    client = make_client()

    with caplog.at_level(logging.ERROR, logger="uvicorn.error"):
        client.get("/boom")

    assert "ValueError" in caplog.text
    assert SECRET_TEXT not in caplog.text


def test_oversized_requests_are_rejected():
    client = make_client()

    assert client.post("/echo", content=b"x" * 500).status_code == 200
    response = client.post("/echo", content=b"x" * 2000)

    assert response.status_code == 413
    assert "too large" in response.json()["detail"]


def test_per_ip_limit_returns_429():
    client = make_client(ip_limiter=SlidingWindowLimiter(limit=3, window_seconds=60))

    statuses = [client.get("/ok").status_code for _ in range(4)]

    assert statuses == [200, 200, 200, 429]
    assert client.get("/ok").headers["Retry-After"].isdigit()


def test_health_check_is_not_rate_limited():
    client = make_client(ip_limiter=SlidingWindowLimiter(limit=1, window_seconds=60))

    statuses = [client.get("/api/v1/health").status_code for _ in range(5)]

    assert statuses == [200] * 5


def test_exception_summary_omits_the_message():
    try:
        raise ValueError(SECRET_TEXT)
    except ValueError as exc:
        summary = summarize_exception(exc)

    assert "ValueError" in summary
    assert "test_exception_summary_omits_the_message" in summary
    assert SECRET_TEXT not in summary