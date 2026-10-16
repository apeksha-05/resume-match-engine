"""Request-level protections applied to every response.

In one place this handles: oversized requests, per-IP rate limiting, safe
handling of unexpected errors, and standard security headers.
"""

import logging
import traceback
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.core.rate_limit import SlidingWindowLimiter

logger = logging.getLogger("uvicorn.error")

# Never rate limited, so the hosting platform's health checks cannot be blocked.
RATE_LIMIT_EXEMPT_PATHS = {"/api/v1/health"}

GENERIC_ERROR_MESSAGE = "Something went wrong on the server. Please try again."


def summarize_exception(exc: BaseException) -> str:
    """Says what went wrong and where, but NOT the exception's message.

    Messages can contain user data: for example, validation errors echo the
    values that failed. Leaving them out keeps resume text out of the logs.
    """
    frames = traceback.extract_tb(exc.__traceback__)
    if not frames:
        return type(exc).__name__
    last = frames[-1]
    return f"{type(exc).__name__} at {last.filename}:{last.lineno} in {last.name}"


def _add_security_headers(response: Response, production: bool) -> None:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Cache-Control", "no-store")
    if production:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )


def install_security_middleware(
    app: FastAPI,
    *,
    max_request_bytes: int,
    ip_limiter: SlidingWindowLimiter | None,
    production: bool,
    log_tracebacks: bool,
) -> None:
    def reject_early(request: Request) -> Response | None:
        content_length = request.headers.get("content-length", "")
        if content_length.isdigit() and int(content_length) > max_request_bytes:
            return JSONResponse(status_code=413, content={"detail": "The request is too large."})

        if ip_limiter is not None and request.url.path not in RATE_LIMIT_EXEMPT_PATHS:
            host = request.client.host if request.client else "unknown"
            retry_after = ip_limiter.hit(host)
            if retry_after:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Too many requests. Please wait {retry_after} seconds and try again."
                    },
                    headers={"Retry-After": str(retry_after)},
                )
        return None

    @app.middleware("http")
    async def protect(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = reject_early(request)
        if response is None:
            try:
                response = await call_next(request)
            except Exception as exc:
                if log_tracebacks:
                    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
                else:
                    logger.error(
                        "Unhandled error on %s %s: %s",
                        request.method,
                        request.url.path,
                        summarize_exception(exc),
                    )
                response = JSONResponse(status_code=500, content={"detail": GENERIC_ERROR_MESSAGE})

        _add_security_headers(response, production)
        return response
