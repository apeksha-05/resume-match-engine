import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.account import AccountSummaryOut


def _count(
    db: Session, model: type[Resume] | type[Analysis] | type[JobDescription], user_id: uuid.UUID
) -> int:
    statement = select(func.count()).select_from(model).where(model.user_id == user_id)
    return db.execute(statement).scalar_one()


def get_account_summary(db: Session, user_id: uuid.UUID) -> AccountSummaryOut:
    return AccountSummaryOut(
        resumes=_count(db, Resume, user_id),
        analyses=_count(db, Analysis, user_id),
        job_descriptions=_count(db, JobDescription, user_id),
    )


def delete_user_data(db: Session, user_id: uuid.UUID) -> None:
    """Permanently deletes everything stored for this user, in one transaction.

    Analyses go first because they reference resumes and job descriptions.
    Resume chunks are removed by the database's ON DELETE CASCADE rule.
    """
    try:
        db.execute(delete(Analysis).where(Analysis.user_id == user_id))
        db.execute(delete(JobDescription).where(JobDescription.user_id == user_id))
        db.execute(delete(Resume).where(Resume.user_id == user_id))
        db.commit()
    except Exception:
        db.rollback()
        raise
