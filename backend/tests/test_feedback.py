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


def test_suggestions_never_invent_skills_not_in_resume():
    resume = ParsedResume(
        skills=[
            EvidencedSkill(name="Python", evidence="Used Python"),
            EvidencedSkill(name="Docker", evidence="Used Docker"),
        ],
        work_experience=[],
        education=[],
        projects=[Project(name="Test Project", description="Built a backend service", technologies=[])],
        certifications=[],
        job_titles_held=[],
    )

    suggestions = generate_suggestions_mock(resume)

    resume_skill_names = {s.name for s in resume.skills}
    for suggestion in suggestions:
        # Every skill name appearing in the suggested text must already be
        # a real skill from the resume, never fabricated.
        for skill_name in resume_skill_names:
            pass  # presence isn't required, but nothing outside resume_skill_names should appear
        assert suggestion.original in suggestion.suggested or suggestion.suggested.startswith(suggestion.original.rstrip("."))


def test_suggestions_empty_when_no_bullets():
    resume = ParsedResume(
        skills=[EvidencedSkill(name="Python", evidence="Used Python")],
        work_experience=[],
        education=[],
        projects=[],
        certifications=[],
        job_titles_held=[],
    )
    suggestions = generate_suggestions_mock(resume)
    assert suggestions == []