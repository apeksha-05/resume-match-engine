"""A mock stand-in for real LLM-based resume extraction.

This exists so the rest of the application (scoring, recommendations, the
frontend, etc.) can be built and tested end-to-end without requiring a paid
or currently-accessible LLM API key. It is NOT real language understanding,
it does case-insensitive keyword matching against the canonical skill list,
grounded in real evidence snippets copied from the actual resume text.

Swap to real AI at any time: set GEMINI_API_KEY in .env (see
app/services/resume_extraction.py). No other code needs to change.
"""

import re

from app.core.skills_data import SKILLS
from app.schemas.resume import EvidencedSkill, ParsedResume

# Build a flat lookup of every searchable term (canonical names + aliases)
# pointing back to its canonical name.
_SEARCH_TERMS: dict[str, str] = {}
for canonical_name, (_category, aliases) in SKILLS.items():
    _SEARCH_TERMS[canonical_name.lower()] = canonical_name
    for alias in aliases:
        _SEARCH_TERMS[alias.lower()] = canonical_name

EVIDENCE_CONTEXT_CHARS = 60  # characters of surrounding text to use as evidence


def _find_evidence_snippet(text: str, term: str) -> str | None:
    """Finds the term in the text (case-insensitive, whole-word) and returns
    a short surrounding snippet as evidence. Returns None if not found."""
    pattern = r"\b" + re.escape(term) + r"\b"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None:
        return None

    start = max(0, match.start() - EVIDENCE_CONTEXT_CHARS)
    end = min(len(text), match.end() + EVIDENCE_CONTEXT_CHARS)
    snippet = text[start:end].strip()
    # Collapse internal newlines/whitespace for a cleaner evidence string.
    return " ".join(snippet.split())


def extract_structured_resume_mock(resume_text: str) -> ParsedResume:
    """Produces a ParsedResume using keyword matching instead of an LLM.

    Only the `skills` field is populated with any confidence, since reliably
    identifying work experience, education, and projects from free-form text
    genuinely requires language understanding, that's exactly what the real
    Gemini/Claude integration (resume_extraction.py) is for. This mock exists
    to unblock development, not to replace real extraction.
    """
    found_skills: list[EvidencedSkill] = []
    seen_canonical_names: set[str] = set()

    for term, canonical_name in _SEARCH_TERMS.items():
        if canonical_name in seen_canonical_names:
            continue
        snippet = _find_evidence_snippet(resume_text, term)
        if snippet:
            found_skills.append(EvidencedSkill(name=canonical_name, evidence=snippet))
            seen_canonical_names.add(canonical_name)

    return ParsedResume(
        skills=found_skills,
        work_experience=[],
        education=[],
        projects=[],
        certifications=[],
        job_titles_held=[],
    )