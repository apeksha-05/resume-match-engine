import pytest

from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import EvidencedSkill, ParsedResume
from app.services.scoring import _score_skills
from app.services.skill_normalization import (
    normalize_parsed_jd,
    normalize_parsed_resume,
    normalize_skill,
    normalize_skill_list,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("js", "JavaScript"),
        ("JS", "JavaScript"),
        ("py", "Python"),
        ("Postgres", "PostgreSQL"),
        ("k8s", "Kubernetes"),
        ("react.js", "React"),
        ("Amazon Web Services", "AWS"),
        ("ci cd", "CI/CD"),
        ("C Plus Plus", "C++"),
    ],
)
def test_aliases_map_to_the_canonical_name(raw: str, expected: str):
    assert normalize_skill(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [("python", "Python"), ("rest apis", "REST APIs"), ("aws", "AWS")],
)
def test_canonical_names_get_their_proper_casing(raw: str, expected: str):
    assert normalize_skill(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [("  Python. ", "Python"), ("(SQL)", "SQL"), ("Node.js.", "Node.js")],
)
def test_whitespace_and_punctuation_are_cleaned(raw: str, expected: str):
    assert normalize_skill(raw) == expected


def test_a_leading_dot_is_kept():
    assert normalize_skill(".NET") == ".NET"


def test_unknown_skills_keep_their_spelling():
    assert normalize_skill("Terraform") == "Terraform"
    assert normalize_skill("terraform") == "terraform"


def test_empty_names_become_empty():
    assert normalize_skill("   ") == ""


def test_lists_are_deduplicated_and_empty_names_dropped():
    assert normalize_skill_list(["JS", "JavaScript", "js", "", "  "]) == ["JavaScript"]


def test_normalizing_twice_changes_nothing():
    for raw in ["js", "Postgres", "Terraform", "  Python. ", ".NET", "REST API"]:
        once = normalize_skill(raw)
        assert normalize_skill(once) == once


def test_resume_skills_are_merged_keeping_the_first_evidence():
    parsed = ParsedResume(
        skills=[
            EvidencedSkill(name="js", evidence="evidence one"),
            EvidencedSkill(name="JavaScript", evidence="evidence two"),
            EvidencedSkill(name="py", evidence="evidence three"),
        ]
    )

    result = normalize_parsed_resume(parsed)

    assert [s.name for s in result.skills] == ["JavaScript", "Python"]
    assert result.skills[0].evidence == "evidence one"


def test_a_skill_required_and_preferred_stays_only_under_required():
    parsed = ParsedJobDescription(
        title="Backend Engineer",
        required_skills=["js", "Python"],
        preferred_skills=["JavaScript", "Redis", "redis"],
    )

    result = normalize_parsed_jd(parsed)

    assert result.required_skills == ["JavaScript", "Python"]
    assert result.preferred_skills == ["Redis"]


def make_resume(*names: str) -> ParsedResume:
    return ParsedResume(skills=[EvidencedSkill(name=n, evidence=f"used {n}") for n in names])


def make_jd(required: list[str], preferred: list[str] | None = None) -> ParsedJobDescription:
    return ParsedJobDescription(
        title="Backend Engineer",
        required_skills=required,
        preferred_skills=preferred or [],
        responsibilities=[],
        min_years_experience=None,
        education_requirement=None,
    )


def test_a_resume_alias_matches_a_canonical_requirement():
    score, _, details = _score_skills(make_resume("JS"), make_jd(["JavaScript"]))

    assert score == 1.0
    assert [m.name for m in details["matched_required"]] == ["JavaScript"]
    assert details["missing_required"] == []


def test_unknown_skills_match_regardless_of_case():
    score, _, _ = _score_skills(make_resume("terraform"), make_jd(["Terraform"]))

    assert score == 1.0


def test_a_skill_listed_as_required_and_preferred_counts_once_as_required():
    _, _, details = _score_skills(make_resume("Python"), make_jd(["Python"], ["python", "Redis"]))

    assert [m.name for m in details["matched_required"]] == ["Python"]
    assert details["matched_preferred"] == []
    assert details["missing_preferred"] == ["Redis"]
