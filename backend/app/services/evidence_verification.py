from app.schemas.resume import ParsedResume


def filter_unverified_skills(parsed: ParsedResume, original_text: str) -> ParsedResume:
    """Removes any skill whose evidence snippet cannot actually be found in the
    original resume text. This guards against the AI paraphrasing instead of quoting,
    or in rare cases, inventing a skill despite instructions not to."""

    normalized_text = " ".join(original_text.lower().split())

    verified_skills = []
    for skill in parsed.skills:
        normalized_evidence = " ".join(skill.evidence.lower().split())
        if normalized_evidence and normalized_evidence in normalized_text:
            verified_skills.append(skill)

    parsed.skills = verified_skills
    return parsed