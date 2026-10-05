"""Heuristics for estimating years of experience and comparing job titles.
These are deliberately simple, exact date-range math from free-text resumes
is inherently ambiguous. Documented as a best-effort estimate, not a precise
calculation.
"""

import re
from datetime import datetime

_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
_PRESENT_PATTERN = re.compile(r"\b(present|current|now)\b", re.IGNORECASE)


def estimate_years_from_duration(duration_text: str) -> float:
    """Estimates years spanned by a duration string like 'Jan 2023 - Present'
    or '2021-2023'. Returns 0 if it can't confidently parse two points in time.
    """
    years_found = [int(match.group()) for match in _YEAR_PATTERN.finditer(duration_text)]

    if _PRESENT_PATTERN.search(duration_text) and years_found:
        start_year = min(years_found)
        return max(0.0, datetime.now().year - start_year)

    if len(years_found) >= 2:
        return max(0.0, max(years_found) - min(years_found))

    return 0.0


def total_relevant_years(durations: list[str]) -> float:
    """Sums estimated years across all work experience entries.
    Does not account for overlapping date ranges; treats each entry
    independently, a reasonable simplification for an estimate."""
    return sum(estimate_years_from_duration(d) for d in durations)