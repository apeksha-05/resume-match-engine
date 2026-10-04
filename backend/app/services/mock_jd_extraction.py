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

# Words that, when found near a skill mention, suggest it's a "nice to have"
# rather than a hard requirement. Deliberately simple; a real LLM (once a
# working key is available) will do this far more reliably.
PREFERRED_MARKERS = ["preferred", "nice to have", "bonus", "a plus", "good to have"]


def _skills_mentioned(text: str) -> set[str]:
    found = set()
    for term, canonical_name in _SEARCH_TERMS.items():
        if re.search(r"\b" + re.escape(term) + r"\b", text, flags=re.IGNORECASE):
            found.add(canonical_name)
    return found


def extract_structured_jd_mock(jd_text: str) -> ParsedJobDescription:
    lower_text = jd_text.lower()

    # Split into a "preferred section" (after a preferred-marker word) and
    # everything else, treated as required. This is a rough heuristic.
    split_index = len(jd_text)
    for marker in PREFERRED_MARKERS:
        idx = lower_text.find(marker)
        if idx != -1:
            split_index = min(split_index, idx)

    required_text = jd_text[:split_index]
    preferred_text = jd_text[split_index:]

    required_skills = sorted(_skills_mentioned(required_text))
    preferred_skills = sorted(_skills_mentioned(preferred_text) - set(required_skills))

    # Best-effort title guess: first non-empty line, truncated.
    first_line = next((line.strip() for line in jd_text.splitlines() if line.strip()), "Untitled role")
    title_guess = first_line[:100]

    years_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", jd_text, flags=re.IGNORECASE)
    min_years = int(years_match.group(1)) if years_match else None

    return ParsedJobDescription(
        title=title_guess,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=[],  # left empty; identifying real responsibility sentences needs real language understanding
        min_years_experience=min_years,
        education_requirement=None,
    )