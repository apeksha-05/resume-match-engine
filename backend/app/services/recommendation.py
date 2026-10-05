from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job_description import ParsedJobDescription
from app.schemas.job import JobOut
from app.schemas.recommendation import JobRecommendationOut
from app.schemas.resume import ParsedResume
from app.services.scoring import compute_analysis


def _job_to_parsed_jd(job: Job) -> ParsedJobDescription:
    """Builds a ParsedJobDescription from a saved Job row, so the recommender
    reuses the exact same scoring engine as the resume-vs-JD analysis flow,
    per the Phase 2 requirement that recommendations use the same matching logic."""
    return ParsedJobDescription(
        title=job.title,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        responsibilities=[job.description] if job.description else [],
        min_years_experience=job.min_years or None,
        education_requirement=None,
    )


def recommend_jobs(
    db: Session,
    resume: ParsedResume,
    work_mode: str | None = None,
    max_years: int | None = None,
    limit: int = 10,
) -> list[JobRecommendationOut]:
    stmt = select(Job)
    if work_mode:
        stmt = stmt.where(Job.work_mode == work_mode)
    if max_years is not None:
        stmt = stmt.where(Job.min_years <= max_years)

    jobs = db.execute(stmt).scalars().all()

    recommendations: list[JobRecommendationOut] = []
    for job in jobs:
        parsed_jd = _job_to_parsed_jd(job)
        result = compute_analysis(resume, parsed_jd)

        matched_skills = sorted(
            {s.name for s in result.matched_required} | {s.name for s in result.matched_preferred}
        )
        missing_skills = sorted(set(result.missing_required) | set(result.missing_preferred))

        recommendations.append(
            JobRecommendationOut(
                job=JobOut.model_validate(job),
                score=result.overall_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
            )
        )

    recommendations.sort(key=lambda r: r.score, reverse=True)
    return recommendations[:limit]