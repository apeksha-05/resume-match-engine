from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.rate_limit import SlidingWindowLimiter
from app.core.security_middleware import install_security_middleware
from app.routers import (
    account,
    analyses,
    config,
    health,
    job_descriptions,
    jobs,
    me,
    recommendations,
    resumes,
)

settings = get_settings()

app = FastAPI(title=settings.app_name)

ip_limiter = (
    SlidingWindowLimiter(limit=settings.per_ip_requests_per_minute, window_seconds=60)
    if settings.rate_limit_enabled
    else None
)

# Middleware added LAST is OUTERMOST. The protections go in first (inner) and
# CORS goes in last (outer), so that even their error responses (413, 429, 500)
# carry CORS headers. Otherwise the browser would hide the real message behind
# a generic network error.
install_security_middleware(
    app,
    max_request_bytes=settings.max_request_bytes,
    ip_limiter=ip_limiter,
    production=settings.environment == "production",
    log_tracebacks=settings.environment == "development",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    # We authenticate with bearer tokens, not cookies, so credentials are not needed.
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Retry-After"],
    max_age=600,
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(job_descriptions.router, prefix="/api/v1", tags=["job-descriptions"])
app.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(me.router, prefix="/api/v1", tags=["me"])
app.include_router(account.router, prefix="/api/v1", tags=["account"])