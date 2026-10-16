"""Turns the many ways of writing a skill into one canonical name.

"JS", "js" and "JavaScript" all become "JavaScript". Skills that are not in our
canonical list keep their original spelling, but still compare
case-insensitively. Used when storing extracted data and when scoring.
"""

from app.core.skills_data import SKILLS
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import EvidencedSkill, ParsedResume


def _clean(name: str) -> str:
    """Collapses whitespace, removes surrounding brackets and quotes, and
    trailing punctuation. Leading dots are kept, so '.NET' survives."""
    cleaned = " ".join(name.split())
    cleaned = cleaned.strip("()[]\"'")
    return cleaned.rstrip(".,;:").strip()


_ALIAS_TO_CANONICAL: dict[str, str] = {}
for _canonical, (_category, _aliases) in SKILLS.items():
    _ALIAS_TO_CANONICAL[_clean(_canonical).casefold()] = _canonical
    for _alias in _aliases:
        _ALIAS_TO_CANONICAL[_clean(_alias).casefold()] = _canonical


def normalize_skill(name: str) -> str:
    cleaned = _clean(name)
    return _ALIAS_TO_CANONICAL.get(cleaned.casefold(), cleaned)


def normalize_skill_list(names: list[str]) -> list[str]:
    """Normalizes every name, drops empty ones, and removes duplicates
    (ignoring case) while keeping the original order."""
    result: list[str] = []
    seen: set[str] = set()
    for name in names:
        normalized = normalize_skill(name)
        key = normalized.casefold()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def normalize_parsed_resume(parsed: ParsedResume) -> ParsedResume:
    """Normalizes skill names and merges duplicates, keeping the first evidence."""
    skills: list[EvidencedSkill] = []
    seen: set[str] = set()
    for skill in parsed.skills:
        name = normalize_skill(skill.name)
        key = name.casefold()
        if not name or key in seen:
            continue
        seen.add(key)
        skills.append(EvidencedSkill(name=name, evidence=skill.evidence))
    return parsed.model_copy(update={"skills": skills})


def normalize_parsed_jd(parsed: ParsedJobDescription) -> ParsedJobDescription:
    """Normalizes skill names, removes duplicates, and keeps a skill that is
    listed as both required and preferred only under required."""
    required = normalize_skill_list(parsed.required_skills)
    required_keys = {name.casefold() for name in required}
    preferred = [
        name
        for name in normalize_skill_list(parsed.preferred_skills)
        if name.casefold() not in required_keys
    ]
    return parsed.model_copy(update={"required_skills": required, "preferred_skills": preferred})
