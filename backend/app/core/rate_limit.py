"""Simple in-memory sliding-window rate limiting.

State lives in this process's memory, so it resets when the server restarts
and is not shared between several server instances. That is fine for a
single-instance deployment; several instances would need a shared store such
as Redis.
"""

import math
import threading
import time
import uuid
from collections import deque
from collections.abc import Callable

from fastapi import Depends, HTTPException

from app.core.auth import get_current_user_id
from app.core.config import get_settings


class SlidingWindowLimiter:
    MAX_TRACKED_KEYS = 10_000

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def hit(self, key: str) -> int:
        """Records a request. Returns 0 if it is allowed, otherwise the number
        of seconds the caller should wait before trying again."""
        now = self._clock()
        cutoff = now - self.window_seconds
        with self._lock:
            if len(self._hits) > self.MAX_TRACKED_KEYS:
                self._prune_all(cutoff)
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.limit:
                return max(1, math.ceil(hits[0] + self.window_seconds - now))
            hits.append(now)
            return 0

    def _prune_all(self, cutoff: float) -> None:
        for key in list(self._hits):
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if not hits:
                del self._hits[key]


def limit_per_user(name: str, limit: int, window_seconds: float) -> Callable[..., None]:
    """Builds a FastAPI dependency that limits one endpoint per logged-in user.
    It depends on the login check, so anonymous callers get a 401 first."""
    limiter = SlidingWindowLimiter(limit, window_seconds)

    def dependency(user_id: uuid.UUID = Depends(get_current_user_id)) -> None:
        if not get_settings().rate_limit_enabled:
            return
        retry_after = limiter.hit(f"{name}:{user_id}")
        if retry_after:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Please wait {retry_after} seconds and try again.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency