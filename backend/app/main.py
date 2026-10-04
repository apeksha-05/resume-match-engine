from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import config, health, job_descriptions, jobs, resumes

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(job_descriptions.router, prefix="/api/v1", tags=["job-descriptions"])