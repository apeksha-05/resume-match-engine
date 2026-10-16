import uuid

import pytest
from fastapi import HTTPException

from app.core import rate_limit
from app.core.rate_limit import SlidingWindowLimiter, limit_per_user


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_allows_requests_up_to_the_limit():
    limiter = SlidingWindowLimiter(limit=3, window_seconds=60, clock=FakeClock())

    assert [limiter.hit("a") for _ in range(3)] == [0, 0, 0]


def test_blocks_the_next_request_and_says_how_long_to_wait():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=2, window_seconds=10, clock=clock)

    limiter.hit("a")  # t = 0
    clock.now = 1.0
    limiter.hit("a")
    clock.now = 2.0

    assert limiter.hit("a") == 8  # the first request leaves the window at t = 10


def test_window_slides_so_requests_are_allowed_again():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=2, window_seconds=10, clock=clock)
    limiter.hit("a")
    clock.now = 1.0
    limiter.hit("a")
    assert limiter.hit("a") > 0

    clock.now = 10.5

    assert limiter.hit("a") == 0


def test_keys_are_tracked_independently():
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60, clock=FakeClock())

    assert limiter.hit("alice") == 0
    assert limiter.hit("alice") > 0
    assert limiter.hit("bob") == 0


def test_stale_keys_are_pruned():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=5, window_seconds=10, clock=clock)
    limiter.MAX_TRACKED_KEYS = 2
    for key in ("a", "b", "c"):
        limiter.hit(key)

    clock.now = 100.0
    limiter.hit("d")

    assert len(limiter._hits) == 1


def test_user_dependency_returns_429_when_exceeded(monkeypatch: pytest.MonkeyPatch):
    class Enabled:
        rate_limit_enabled = True

    monkeypatch.setattr(rate_limit, "get_settings", lambda: Enabled())
    dependency = limit_per_user("test-endpoint", limit=1, window_seconds=60)
    user_id = uuid.uuid4()

    dependency(user_id=user_id)  # the first request passes
    with pytest.raises(HTTPException) as error:
        dependency(user_id=user_id)

    assert error.value.status_code == 429
    assert error.value.headers is not None
    assert error.value.headers["Retry-After"].isdigit()


def test_user_dependency_does_nothing_when_disabled(monkeypatch: pytest.MonkeyPatch):
    class Disabled:
        rate_limit_enabled = False

    monkeypatch.setattr(rate_limit, "get_settings", lambda: Disabled())
    dependency = limit_per_user("test-endpoint", limit=1, window_seconds=60)
    user_id = uuid.uuid4()

    for _ in range(5):
        dependency(user_id=user_id)  # never raises
