from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import EvidencedSkill, ParsedResume, Project, WorkExperience
from app.schemas.analysis import Weights
from app.services.scoring import compute_analysis

EQUAL_WEIGHTS = Weights(skills=0.25, semantic=0.25, experience=0.25, education=0.25)


def make_resume(skills: list[str], evidence: str = "mentioned in resume") -> ParsedResume:
    return ParsedResume(
        skills=[EvidencedSkill(name=s, evidence=evidence) for s in skills],
        work_experience=[],
        education=[],
        projects=[],
        certifications=[],
        job_titles_held=[],
    )


def make_jd(required: list[str], preferred: list[str] | None = None) -> ParsedJobDescription:
    return ParsedJobDescription(
        title="Backend Engineer",
        required_skills=required,
        preferred_skills=preferred or [],
        responsibilities=[],
        min_years_experience=None,
        education_requirement=None,
    )


def test_perfect_skill_match_scores_high():
    resume = make_resume(["Python", "SQL", "Docker"])
    jd = make_jd(required=["Python", "SQL", "Docker"])

    result = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    skills_category = next(c for c in result.categories if c.key == "skills")
    assert skills_category.score == 1.0
    assert sorted(s.name for s in result.matched_required) == ["Docker", "Python", "SQL"]
    assert result.missing_required == []


def test_partial_skill_match_is_proportional():
    resume = make_resume(["Python"])
    jd = make_jd(required=["Python", "SQL", "Docker", "AWS"])

    result = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    skills_category = next(c for c in result.categories if c.key == "skills")
    assert skills_category.score == 0.25  # 1 of 4 required skills
    assert result.missing_required == ["AWS", "Docker", "SQL"]


def test_no_overlap_scores_zero_on_skills():
    resume = make_resume(["Java", "Spring"])
    jd = make_jd(required=["Python", "FastAPI"])

    result = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    skills_category = next(c for c in result.categories if c.key == "skills")
    assert skills_category.score == 0.0


def test_missing_education_requirement_is_marked_not_applicable():
    resume = make_resume(["Python"])
    jd = make_jd(required=["Python"])  # no education_requirement set

    result = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    education_category = next(c for c in result.categories if c.key == "education")
    assert education_category.applicable is False
    assert education_category.weight == 0.0
    assert any("education" in note.lower() for note in result.calculation_notes)


def test_weight_redistribution_sums_effective_weights_to_one():
    resume = make_resume(["Python"])
    jd = make_jd(required=["Python"])  # education will be N/A

    result = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    applicable_weights = sum(c.weight for c in result.categories if c.applicable)
    assert abs(applicable_weights - 1.0) < 0.01


def test_overall_score_is_between_0_and_100():
    resume = make_resume(["Python", "React"])
    jd = make_jd(required=["Python", "Docker", "AWS"], preferred=["Redis"])

    result = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    assert 0 <= result.overall_score <= 100


def test_scoring_is_deterministic():
    resume = make_resume(["Python", "SQL"])
    jd = make_jd(required=["Python", "SQL", "Docker"])

    result_1 = compute_analysis(resume, jd, EQUAL_WEIGHTS)
    result_2 = compute_analysis(resume, jd, EQUAL_WEIGHTS)

    assert result_1.overall_score == result_2.overall_score
    assert result_1.categories[0].score == result_2.categories[0].score


def test_default_weights_are_used_when_none_provided():
    resume = make_resume(["Python"])
    jd = make_jd(required=["Python"])

    result = compute_analysis(resume, jd, weights=None)

    assert result.weights.skills == 0.45  # Phase 2 default