from typing import Any

from app.schemas.resume import ResumeSummaryOut


def to_resume_summary(row: Any) -> ResumeSummaryOut:
    """Builds a summary from a stored Resume row. Kept free of database
    imports so it can be unit-tested without a database."""
    skills = (row.parsed or {}).get("skills", [])
    return ResumeSummaryOut(
        id=row.id,
        filename=row.filename,
        created_at=row.created_at,
        skill_count=len(skills),
    )