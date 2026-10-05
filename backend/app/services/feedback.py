from app.schemas.feedback import AnalysisFullResult
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume
from app.schemas.analysis import Weights
from app.services.mock_roadmap import generate_roadmap_mock
from app.services.mock_suggestions import generate_suggestions_mock
from app.services.scoring import compute_analysis


def compute_full_analysis(
    resume: ParsedResume,
    jd: ParsedJobDescription,
    weights: Weights | None = None,
) -> AnalysisFullResult:
    """Computes the deterministic score plus suggestions and a learning
    roadmap. Suggestions and roadmap use mock generation today; swap to
    real AI by branching on settings.use_mock_llm here, following the same
    pattern as app/services/resume_extraction.py."""
    score_result = compute_analysis(resume, jd, weights)

    suggestions = generate_suggestions_mock(resume)
    missing_required_names = score_result.missing_required
    roadmap = generate_roadmap_mock(missing_required_names)

    return AnalysisFullResult(
        **score_result.model_dump(),
        suggestions=suggestions,
        roadmap=roadmap,
    )