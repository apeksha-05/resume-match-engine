"""Mock resume bullet suggestions.

Honesty constraint carried over from Phase 2: suggestions must never invent
skills, metrics, or achievements. This mock only rephrases bullets using
words already present elsewhere in the resume (skill names the person
already listed), never introducing new claims. A real LLM integration
(swap in later, following the same pattern as resume_extraction.py) could
produce more natural phrasing, but must follow this same no-fabrication rule.
"""

from app.schemas.feedback import BulletSuggestion
from app.schemas.resume import ParsedResume

MAX_SUGGESTIONS = 4


def _gather_bullets(resume: ParsedResume) -> list[str]:
    bullets: list[str] = []
    for project in resume.projects:
        if project.description:
            bullets.append(project.description)
    for job in resume.work_experience:
        bullets.extend(job.responsibilities)
    return bullets


def generate_suggestions_mock(resume: ParsedResume) -> list[BulletSuggestion]:
    bullets = _gather_bullets(resume)
    resume_skill_names = [s.name for s in resume.skills]

    suggestions: list[BulletSuggestion] = []
    for bullet in bullets[:MAX_SUGGESTIONS]:
        # Find skills already in resume.skills that are mentioned in this
        # bullet's general vicinity but not explicitly named in the bullet
        # itself, and suggest naming them explicitly. We only ever use
        # skill names the person already listed elsewhere, never new ones.
        mentioned_elsewhere = [
            name for name in resume_skill_names
            if name.lower() not in bullet.lower()
        ]

        if not mentioned_elsewhere:
            continue

        # Mock heuristic: suggest naming the resume's #1 listed skill if it's
        # not already in this bullet. A real LLM would pick more contextually.
        candidate_skill = mentioned_elsewhere[0]
        suggested = f"{bullet.rstrip('.')} (using {candidate_skill})."

        suggestions.append(
            BulletSuggestion(
                original=bullet,
                suggested=suggested,
                why_changed=(
                    f"Explicitly names '{candidate_skill}', which you already listed as a "
                    f"skill elsewhere in your resume. Only keep this if it's accurate for this bullet."
                ),
            )
        )

    return suggestions