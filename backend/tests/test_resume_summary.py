import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.resume_summary import to_resume_summary


def make_row(parsed: dict) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        filename="resume.pdf",
        created_at=datetime.now(timezone.utc),
        parsed=parsed,
    )


def test_summary_counts_skills():
    row = make_row(
        {
            "skills": [
                {"name": "Python", "evidence": "Used Python"},
                {"name": "SQL", "evidence": "Wrote SQL"},
            ]
        }
    )

    assert to_resume_summary(row).skill_count == 2


def test_summary_handles_missing_skills_key():
    assert to_resume_summary(make_row({})).skill_count == 0


def test_summary_keeps_identity_fields():
    row = make_row({"skills": []})

    summary = to_resume_summary(row)

    assert summary.id == row.id
    assert summary.filename == "resume.pdf"
    assert summary.created_at == row.created_at