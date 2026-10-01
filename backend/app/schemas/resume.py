from pydantic import BaseModel


class ResumeTextExtractionOut(BaseModel):
    """Temporary response while we build the pipeline step by step.
    Replaced by the full structured resume schema in Phase 5B."""

    filename: str
    word_count: int
    preview: str  # first ~500 characters, just so we can see something worked