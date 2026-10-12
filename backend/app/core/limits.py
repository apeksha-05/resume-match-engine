"""Per-user limits for the expensive endpoints (each allows N requests per hour)."""

from app.core.rate_limit import limit_per_user

limit_uploads = limit_per_user("upload", 20, 3600)
limit_analyses = limit_per_user("analysis", 30, 3600)
limit_recommendations = limit_per_user("recommendation", 30, 3600)
limit_reports = limit_per_user("report", 60, 3600)
limit_account_changes = limit_per_user("account", 10, 3600)
limit_job_descriptions = limit_per_user("job-description", 60, 3600)