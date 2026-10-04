"""Mock job description extraction, mirroring mock_resume_extraction.py.
Uses keyword matching against the canonical skill list rather than real
language understanding. See mock_resume_extraction.py for the full rationale.
"""

import re

from app.core.skills_data import SKILLS
from app.schemas.job_description import ParsedJobDescription

_SEARCH_TERMS: dict[str, str] = {}
for canonical_name, (_category, aliases) in SKILLS.items():
    _SEARCH_TERMS[canonical_name.lower()] = canonical_name
    for alias in aliases:
        _SEARCH_TERMS[alias.lower()] = canonical_name

# Words that, when found in the same sentence as a skill mention, suggest
# it's a "nice to have" rather than a hard requirement. Deliberately simple;
# a real LLM (once a working key is available) will do this far more reliably.
PREFERRED_MARKERS = ["preferred", "nice to have", "bonus", "a plus", "good to have"]


def _skills_mentioned(text: str) -> set[str]:
    found = set()
    for term, canonical_name in _SEARCH_TERMS.items():
        if re.search(r"\b" + re.escape(term) + r"\b", text, flags=re.IGNORECASE):
            found.add(canonical_name)
    return found


def _split_sentences(text: str) -> list[str]:
    # Simple sentence splitter: good enough for mock-mode JD parsing.
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def extract_structured_jd_mock(jd_text: str) -> ParsedJobDescription:
    sentences = _split_sentences(jd_text)

    required_skills: set[str] = set()
    preferred_skills: set[str] = set()

    for sentence in sentences:
        lower_sentence = sentence.lower()
        skills_here = _skills_mentioned(sentence)
        is_preferred_sentence = any(marker in lower_sentence for marker in PREFERRED_MARKERS)

        if is_preferred_sentence:
            preferred_skills.update(skills_here)
        else:
            required_skills.update(skills_here)

    # A skill should not appear in both lists; preferred mentions win, since
    # that's the more specific/explicit signal.
    required_skills -= preferred_skills

    first_line = next((line.strip() for line in jd_text.splitlines() if line.strip()), "Untitled role")
    title_guess = first_line[:100]

    years_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", jd_text, flags=re.IGNORECASE)
    min_years = int(years_match.group(1)) if years_match else None

    return ParsedJobDescription(
        title=title_guess,
        required_skills=sorted(required_skills),
        preferred_skills=sorted(preferred_skills),
        responsibilities=[],
        min_years_experience=min_years,
        education_requirement=None,
    )