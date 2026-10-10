import uuid
from datetime import datetime, timezone

import pymupdf

from app.schemas.analysis import CategoryScore, EvidenceItem, SkillMatch, Weights
from app.schemas.analysis_records import AnalysisDetailOut
from app.schemas.feedback import BulletSuggestion, RoadmapItem
from app.services.report_pdf import build_report_pdf


def make_detail(
    job_title: str = "Backend Engineer",
    company: str = "Acme Cloud",
    is_demo: bool = False,
    snippet: str = "Built APIs in Python",
) -> AnalysisDetailOut:
    return AnalysisDetailOut(
        id=uuid.uuid4(),
        job_title=job_title,
        company=company,
        is_demo=is_demo,
        created_at=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
        overall_score=71,
        weights=Weights(skills=0.45, semantic=0.25, experience=0.2, education=0.1),
        categories=[
            CategoryScore(
                key="skills",
                label="Skills coverage",
                score=0.667,
                weight=0.5,
                applicable=True,
                explanation="4 of 6 required skills matched.",
            ),
            CategoryScore(
                key="education",
                label="Education alignment",
                score=0.0,
                weight=0.0,
                applicable=False,
                explanation="No education requirement stated.",
            ),
        ],
        matched_required=[SkillMatch(name="Python", evidence=snippet)],
        missing_required=["Docker"],
        matched_preferred=[],
        missing_preferred=["Redis"],
        evidence=[EvidenceItem(requirement="Python", snippet=snippet, similarity=0.61)],
        calculation_notes=["Overall score = 100 x weighted sum of category scores."],
        suggestions=[
            BulletSuggestion(
                original="Worked on backend.",
                suggested="Built backend APIs (using Python).",
                why_changed="Names a skill already on your resume.",
            )
        ],
        roadmap=[
            RoadmapItem(
                skill="Docker",
                reason="Required and not shown on your resume.",
                steps=["Install Docker.", "Write a Dockerfile."],
                estimated_weeks=2,
            )
        ],
    )


def pdf_text(pdf_bytes: bytes) -> str:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        text = " ".join(page.get_text() for page in document)
    return " ".join(text.split())


def test_report_is_a_valid_pdf():
    pdf_bytes = build_report_pdf(make_detail())

    assert pdf_bytes.startswith(b"%PDF-")
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        assert document.page_count >= 1


def test_report_contains_the_key_content():
    text = pdf_text(build_report_pdf(make_detail()))

    assert "Backend Engineer" in text
    assert "Acme Cloud" in text
    assert "71" in text
    assert "Skills coverage" in text
    assert "Docker" in text
    assert "Redis" in text
    assert "not a hiring probability" in text


def test_report_marks_demo_data():
    text = pdf_text(build_report_pdf(make_detail(is_demo=True)))

    assert "DEMO DATA" in text


def test_report_has_no_demo_label_for_real_analyses():
    text = pdf_text(build_report_pdf(make_detail(is_demo=False)))

    assert "DEMO DATA" not in text


def test_markup_in_user_text_is_shown_literally():
    detail = make_detail(job_title="<b>Evil & Co</b>", snippet="<i>x</i> & y")

    text = pdf_text(build_report_pdf(detail))

    assert "<b>Evil & Co</b>" in text
    assert "&amp;" not in text


def test_unsupported_characters_do_not_break_the_report():
    detail = make_detail(company="Café 日本語 🙂", snippet="Built APIs 日本語")

    pdf_bytes = build_report_pdf(detail)

    assert pdf_bytes.startswith(b"%PDF-")
    assert "Caf" in pdf_text(pdf_bytes)


def test_very_long_user_text_is_clipped_and_still_renders():
    detail = make_detail(snippet="word " * 2000)

    pdf_bytes = build_report_pdf(detail)

    assert pdf_bytes.startswith(b"%PDF-")