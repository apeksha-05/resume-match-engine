import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.analysis import CategoryScore, EvidenceItem, SkillMatch, Weights
from app.schemas.analysis_records import AnalysisCreateIn
from app.schemas.feedback import AnalysisFullResult, BulletSuggestion, RoadmapItem
from app.services.analysis_records import (
    pack_analysis,
    short_title,
    to_history_item,
    unpack_analysis,
)

LONG_TEXT = "x" * 60


def make_full_result() -> AnalysisFullResult:
    return AnalysisFullResult(
        overall_score=71,
        weights=Weights(skills=0.45, semantic=0.25, experience=0.2, education=0.1),
        categories=[
            CategoryScore(
                key="skills", label="Skills coverage", score=0.667, weight=0.5,
                applicable=True, explanation="4 of 6 required skills matched.",
            ),
            CategoryScore(
                key="education", label="Education alignment", score=0.0, weight=0.0,
                applicable=False, explanation="No education requirement stated.",
            ),
        ],
        matched_required=[SkillMatch(name="Python", evidence="Built APIs in Python")],
        missing_required=["Docker"],
        matched_preferred=[],
        missing_preferred=["Redis"],
        evidence=[
            EvidenceItem(requirement="Python", snippet="Built APIs in Python", similarity=0.61)
        ],
        calculation_notes=["note one"],
        suggestions=[BulletSuggestion(original="a", suggested="b", why_changed="c")],
        roadmap=[RoadmapItem(skill="Docker", reason="r", steps=["s1"], estimated_weeks=2)],
    )


def make_row(full: AnalysisFullResult) -> SimpleNamespace:
    fields = pack_analysis(full, "Backend Engineer", "Acme Cloud", True)
    return SimpleNamespace(id=uuid.uuid4(), created_at=datetime.now(timezone.utc), **fields)


def test_pack_then_unpack_round_trips():
    full = make_full_result()
    row = make_row(full)

    detail = unpack_analysis(row)

    assert detail.id == row.id
    assert detail.job_title == "Backend Engineer"
    assert detail.company == "Acme Cloud"
    assert detail.is_demo is True
    assert detail.overall_score == 71
    assert detail.categories == full.categories
    assert detail.missing_required == ["Docker"]
    assert detail.matched_required[0].name == "Python"
    assert detail.roadmap[0].skill == "Docker"
    assert detail.suggestions[0].original == "a"


def test_history_item_has_summary_fields():
    row = make_row(make_full_result())

    item = to_history_item(row)

    assert item.id == row.id
    assert item.job_title == "Backend Engineer"
    assert item.company == "Acme Cloud"
    assert item.overall_score == 71


def test_short_title_uses_first_sentence():
    assert short_title("Backend Engineer at Acme Cloud. We need Python.") == "Backend Engineer at Acme Cloud"


def test_short_title_truncates_long_text():
    result = short_title("A" * 200)
    assert len(result) <= 80
    assert result.endswith("...")


def test_short_title_handles_empty_text():
    assert short_title("   ") == "Untitled role"


def test_create_requires_a_target():
    with pytest.raises(ValidationError):
        AnalysisCreateIn(resume_id=uuid.uuid4())


def test_create_rejects_both_targets():
    with pytest.raises(ValidationError):
        AnalysisCreateIn(
            resume_id=uuid.uuid4(), job_description_text=LONG_TEXT, job_id=uuid.uuid4()
        )


def test_create_accepts_text_only():
    payload = AnalysisCreateIn(resume_id=uuid.uuid4(), job_description_text=LONG_TEXT)
    assert payload.job_id is None


def test_create_accepts_job_id_only():
    payload = AnalysisCreateIn(resume_id=uuid.uuid4(), job_id=uuid.uuid4())
    assert payload.job_description_text is None


def test_create_rejects_short_text():
    with pytest.raises(ValidationError):
        AnalysisCreateIn(resume_id=uuid.uuid4(), job_description_text="too short")


def test_create_rejects_negative_weights():
    with pytest.raises(ValidationError):
        AnalysisCreateIn(
            resume_id=uuid.uuid4(),
            job_id=uuid.uuid4(),
            weights=Weights(skills=-0.1, semantic=0.5, experience=0.3, education=0.3),
        )


def test_create_rejects_all_zero_weights():
    with pytest.raises(ValidationError):
        AnalysisCreateIn(
            resume_id=uuid.uuid4(),
            job_id=uuid.uuid4(),
            weights=Weights(skills=0, semantic=0, experience=0, education=0),
        )