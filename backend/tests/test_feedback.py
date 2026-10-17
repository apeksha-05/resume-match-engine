import re

from app.core.skills_data import SKILLS
from app.schemas.resume import EvidencedSkill, ParsedResume, Project
from app.services.mock_roadmap import generate_roadmap_mock
from app.services.mock_suggestions import generate_suggestions_mock


def test_roadmap_generated_for_missing_skills():
    roadmap = generate_roadmap_mock(["Docker", "AWS"])

    assert len(roadmap) == 2
    skill_names = [item.skill for item in roadmap]
    assert "Docker" in skill_names
    assert "AWS" in skill_names
    for item in roadmap:
        assert len(item.steps) > 0
        assert item.estimated_weeks > 0


def test_roadmap_respects_max_items():
    roadmap = generate_roadmap_mock(["Docker", "AWS", "Redis", "Kubernetes", "MongoDB", "GCP"])
    assert len(roadmap) <= 4


def test_roadmap_empty_when_no_missing_skills():
    roadmap = generate_roadmap_mock([])
    assert roadmap == []


def _mentions(skill_name: str, text: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(skill_name) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def test_suggestions_never_invent_skills_not_in_resume():
    resume = ParsedResume(
        skills=[
            EvidencedSkill(name="Python", evidence="Used Python"),
            EvidencedSkill(name="Docker", evidence="Used Docker"),
        ],
        work_experience=[],
        education=[],
        projects=[
            Project(name="Test Project", description="Built a backend service", technologies=[])
        ],
        certifications=[],
        job_titles_held=[],
    )

    suggestions = generate_suggestions_mock(resume)

    assert suggestions, "the sample resume should produce at least one suggestion"
    resume_skill_names = {skill.name for skill in resume.skills}
    for suggestion in suggestions:
        for skill_name in SKILLS:
            added_by_suggestion = _mentions(skill_name, suggestion.suggested) and not _mentions(
                skill_name, suggestion.original
            )
            if added_by_suggestion:
                assert skill_name in resume_skill_names


def test_suggestions_empty_when_no_bullets():
    resume = ParsedResume(
        skills=[EvidencedSkill(name="Python", evidence="Used Python")],
        work_experience=[],
        education=[],
        projects=[],
        certifications=[],
        job_titles_held=[],
    )

    assert generate_suggestions_mock(resume) == []
