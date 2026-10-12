from app.core.config import get_settings
from app.schemas.job_description import ParsedJobDescription
from app.services.mock_jd_extraction import extract_structured_jd_mock
from app.services.skill_normalization import normalize_parsed_jd

settings = get_settings()


class JdExtractionError(Exception):
    """Raised when job description extraction fails."""


def extract_structured_jd(jd_text: str) -> ParsedJobDescription:
    """Extracts structured job description data, then normalizes the skill names.

    Mock today. When a working API key is available, add the real branch here
    following app/services/resume_extraction.py, and wrap the pasted text with
    app/services/prompt_safety.py exactly as the resume path does.
    """
    if settings.use_mock_llm:
        return normalize_parsed_jd(extract_structured_jd_mock(jd_text))
    raise JdExtractionError("Real JD extraction is not yet implemented. Use mock mode for now.")