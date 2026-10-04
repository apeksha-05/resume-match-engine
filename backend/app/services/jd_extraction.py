from app.core.config import get_settings
from app.schemas.job_description import ParsedJobDescription
from app.services.mock_jd_extraction import extract_structured_jd_mock

settings = get_settings()


class JdExtractionError(Exception):
    """Raised when job description extraction fails."""


def extract_structured_jd(jd_text: str) -> ParsedJobDescription:
    """Extracts structured JD data. Mock today; swap to a real LLM call here
    once a working API key is available, following the same pattern as
    app/services/resume_extraction.py."""
    if settings.use_mock_llm:
        return extract_structured_jd_mock(jd_text)
    # Real LLM branch: implement similarly to resume_extraction.py's
    # _extract_structured_resume_real, once a working key is available.
    raise JdExtractionError("Real JD extraction is not yet implemented. Use mock mode for now.")