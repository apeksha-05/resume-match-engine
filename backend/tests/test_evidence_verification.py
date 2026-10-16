from app.schemas.resume import Certification, EvidencedSkill, ParsedResume
from app.services.evidence_verification import filter_unverified_skills

RESUME_TEXT = "Built REST APIs in Python.\nUsed   PostgreSQL for storage."


def make(*skills: tuple[str, str]) -> ParsedResume:
    return ParsedResume(skills=[EvidencedSkill(name=n, evidence=e) for n, e in skills])


def test_a_skill_with_real_evidence_is_kept():
    parsed = make(("Python", "Built REST APIs in Python."))

    result = filter_unverified_skills(parsed, RESUME_TEXT)

    assert [s.name for s in result.skills] == ["Python"]


def test_a_skill_with_invented_evidence_is_dropped():
    parsed = make(("Kubernetes", "Deployed clusters with Kubernetes at scale."))

    result = filter_unverified_skills(parsed, RESUME_TEXT)

    assert result.skills == []


def test_matching_ignores_case_and_whitespace():
    parsed = make(("PostgreSQL", "used postgresql   for\nstorage"))

    result = filter_unverified_skills(parsed, RESUME_TEXT)

    assert [s.name for s in result.skills] == ["PostgreSQL"]


def test_a_skill_with_empty_evidence_is_dropped():
    parsed = make(("Python", ""))

    result = filter_unverified_skills(parsed, RESUME_TEXT)

    assert result.skills == []


def test_other_fields_are_left_alone():
    parsed = ParsedResume(
        skills=[EvidencedSkill(name="Python", evidence="Built REST APIs in Python.")],
        certifications=[Certification(name="AWS Cloud Practitioner")],
    )

    result = filter_unverified_skills(parsed, RESUME_TEXT)

    assert [c.name for c in result.certifications] == ["AWS Cloud Practitioner"]
