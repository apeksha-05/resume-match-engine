"""Helpers for showing untrusted text (resumes, job descriptions) to an AI model.

Two protections. First, the text is wrapped in tags with a random, per-request
name that an attacker cannot know, and anything that looks like our wrapper
tags is stripped out of the text, so the text cannot "close" the wrapper and
start issuing instructions. Second, a simple detector spots obvious attempts
to instruct the AI, so they can be noted in the server log.

These reduce the risk, they do not eliminate it. The real safeguards are
elsewhere: the AI's output must match a strict schema, every skill it reports
must be backed by text that really appears in the resume, and the score is
computed by ordinary code that the resume text cannot influence.
"""

import re
import secrets

_WRAPPER_LOOKALIKE = re.compile(
    r"<\s*/?\s*(?:resume_text|job_description_text)[^>]*>", re.IGNORECASE
)

_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:ignore|disregard|forget)\s+(?:all\s+|any\s+|the\s+|your\s+|my\s+)*"
        r"(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|rules?|context)",
        r"\byou\s+are\s+now\s+(?:a|an|the)\b",
        r"\b(?:give|assign|award|rate)\s+(?:this|the)\s+(?:candidate|resume|applicant)\b",
        r"\b(?:reveal|print|show)\s+(?:your|the)\s+(?:system\s+)?(?:prompt|instructions)",
        r"\bnew\s+instructions?\s*:",
    )
]


def new_boundary(prefix: str) -> str:
    """A tag name that cannot be guessed, for example 'resume_text_9f2c41ab7d03e5b8'."""
    return f"{prefix}_{secrets.token_hex(8)}"


def neutralize_delimiters(text: str) -> str:
    """Replaces anything that looks like one of our wrapper tags."""
    return _WRAPPER_LOOKALIKE.sub("[removed tag]", text)


def build_untrusted_block(text: str, boundary: str) -> str:
    safe = neutralize_delimiters(text).replace(boundary, "[removed]")
    return f"<{boundary}>\n{safe}\n</{boundary}>"


def looks_like_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)
