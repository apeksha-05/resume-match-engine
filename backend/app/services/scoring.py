"""The deterministic, explainable matching engine.

Given a parsed resume and a parsed job description, computes a weighted
overall score (0-100) plus a full, inspectable breakdown by category. This
is NOT an AI call, every number here can be recomputed by hand from the
formula in docs/02-matching-api-and-wireframes.md. Scores are an estimated
fit indicator only, never a hiring probability.
"""

from app.core.weights import DEFAULT_WEIGHTS
from app.schemas.analysis import (
    AnalysisScoreResult,
    CategoryScore,
    EvidenceItem,
    SkillMatch,
    Weights,
)
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume
from app.services.embedding_service import cosine_similarity, embed_texts
from app.services.experience_parsing import total_relevant_years

SIMILARITY_FLOOR = 0.25
SIMILARITY_CEILING = 0.75


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _rescale_similarity(raw_similarity: float) -> float:
    """Maps raw cosine similarity (roughly 0.25-0.75 in practice for
    sentence-transformers) onto a 0-1 scale, as specified in Phase 2."""
    return _clamp01((raw_similarity - SIMILARITY_FLOOR) / (SIMILARITY_CEILING - SIMILARITY_FLOOR))


def _score_skills(resume: ParsedResume, jd: ParsedJobDescription) -> tuple[float | None, str, dict]:
    resume_skill_names = {s.name for s in resume.skills}
    resume_skill_evidence = {s.name: s.evidence for s in resume.skills}

    required = set(jd.required_skills)
    preferred = set(jd.preferred_skills)

    if not required and not preferred:
        return None, "The job description does not list any required or preferred skills.", {}

    matched_required = sorted(required & resume_skill_names)
    missing_required = sorted(required - resume_skill_names)
    matched_preferred = sorted(preferred & resume_skill_names)
    missing_preferred = sorted(preferred - resume_skill_names)

    if required:
        required_ratio = len(matched_required) / len(required)
    else:
        required_ratio = None

    if preferred:
        preferred_ratio = len(matched_preferred) / len(preferred)
    else:
        preferred_ratio = None

    if required_ratio is not None and preferred_ratio is not None:
        score = 0.8 * required_ratio + 0.2 * preferred_ratio
        explanation = (
            f"{len(matched_required)} of {len(required)} required skills matched "
            f"({required_ratio:.0%}), and {len(matched_preferred)} of {len(preferred)} "
            f"preferred skills matched ({preferred_ratio:.0%}). "
            f"Formula: 0.8 x {required_ratio:.2f} + 0.2 x {preferred_ratio:.2f} = {score:.2f}."
        )
    elif required_ratio is not None:
        score = required_ratio
        explanation = (
            f"{len(matched_required)} of {len(required)} required skills matched "
            f"({required_ratio:.0%}). The job description lists no preferred skills."
        )
    else:
        score = preferred_ratio
        explanation = (
            f"{len(matched_preferred)} of {len(preferred)} preferred skills matched "
            f"({preferred_ratio:.0%}). The job description lists no required skills."
        )

    details = {
        "matched_required": [
            SkillMatch(name=name, evidence=resume_skill_evidence.get(name, "")) for name in matched_required
        ],
        "missing_required": missing_required,
        "matched_preferred": [
            SkillMatch(name=name, evidence=resume_skill_evidence.get(name, "")) for name in matched_preferred
        ],
        "missing_preferred": missing_preferred,
    }
    return score, explanation, details


def _resume_chunks(resume: ParsedResume) -> list[str]:
    """Builds a flat list of resume text snippets to compare JD requirements
    against: skill evidence, project descriptions, and job responsibilities."""
    chunks: list[str] = []
    chunks.extend(skill.evidence for skill in resume.skills if skill.evidence)
    chunks.extend(project.description for project in resume.projects if project.description)
    for job in resume.work_experience:
        chunks.extend(job.responsibilities)
    return chunks


def _score_semantic(resume: ParsedResume, jd: ParsedJobDescription) -> tuple[float | None, str, list[EvidenceItem]]:
    requirements = list(jd.required_skills) + list(jd.preferred_skills) + list(jd.responsibilities)
    resume_chunks = _resume_chunks(resume)

    if not requirements or not resume_chunks:
        return None, "Not enough text on one or both sides to compare meaningfully.", []

    requirement_vectors = embed_texts(requirements)
    chunk_vectors = embed_texts(resume_chunks)

    evidence_items: list[EvidenceItem] = []
    rescaled_scores: list[float] = []

    for requirement_text, req_vector in zip(requirements, requirement_vectors):
        best_similarity = -1.0
        best_chunk = ""
        for chunk_text, chunk_vector in zip(resume_chunks, chunk_vectors):
            similarity = cosine_similarity(req_vector, chunk_vector)
            if similarity > best_similarity:
                best_similarity = similarity
                best_chunk = chunk_text

        rescaled = _rescale_similarity(best_similarity)
        rescaled_scores.append(rescaled)
        evidence_items.append(
            EvidenceItem(requirement=requirement_text, snippet=best_chunk, similarity=round(best_similarity, 3))
        )

    score = sum(rescaled_scores) / len(rescaled_scores)
    explanation = (
        f"Compared {len(requirements)} job requirements against {len(resume_chunks)} resume "
        f"passages using local sentence-transformer embeddings, rescaled and averaged. Score: {score:.2f}."
    )
    # Keep only the most informative evidence (highest and lowest matches) to avoid clutter.
    evidence_items.sort(key=lambda item: item.similarity, reverse=True)
    return score, explanation, evidence_items[:5]


def _score_experience(resume: ParsedResume, jd: ParsedJobDescription) -> tuple[float, str]:
    durations = [job.duration for job in resume.work_experience]
    relevant_years = total_relevant_years(durations)
    required_years = jd.min_years_experience

    if not required_years:
        years_component = 1.0
        years_note = "The job description does not specify a required number of years."
    else:
        years_component = _clamp01(relevant_years / required_years)
        years_note = f"Estimated {relevant_years:.1f} relevant years against {required_years} required."

    resume_titles = resume.job_titles_held or [job.job_title for job in resume.work_experience]
    if resume_titles and jd.title:
        title_vectors = embed_texts([jd.title] + resume_titles)
        jd_title_vector, *resume_title_vectors = title_vectors
        title_similarity = max(
            (cosine_similarity(jd_title_vector, v) for v in resume_title_vectors), default=0.0
        )
        title_component = _rescale_similarity(title_similarity)
    else:
        title_component = 0.0

    score = 0.7 * years_component + 0.3 * title_component
    explanation = (
        f"{years_note} Years contributes 0.7 x {years_component:.2f} = {0.7 * years_component:.2f}. "
        f"Title similarity contributes 0.3 x {title_component:.2f} = {0.3 * title_component:.2f}. "
        f"Total: {score:.2f}."
    )
    return score, explanation


def _score_education(resume: ParsedResume, jd: ParsedJobDescription) -> tuple[float | None, str]:
    if not jd.education_requirement:
        return None, "The job description does not specify an education requirement."
    if not resume.education:
        return 0.0, f"The job requires '{jd.education_requirement}', but no education was found on the resume."
    # Simple presence check; a more sophisticated degree-level comparison is a
    # reasonable future improvement once real AI extraction is in place.
    requirement_lower = jd.education_requirement.lower()
    for edu in resume.education:
        if edu.degree.lower() in requirement_lower or requirement_lower in edu.degree.lower():
            return 1.0, f"Resume degree '{edu.degree}' matches the stated requirement."
    return 0.5, "Resume lists education, but it does not clearly match the stated requirement."


def compute_analysis(
    resume: ParsedResume,
    jd: ParsedJobDescription,
    weights: Weights | None = None,
) -> AnalysisScoreResult:
    weights = weights or Weights(**DEFAULT_WEIGHTS)

    skills_score, skills_explanation, skills_details = _score_skills(resume, jd)
    semantic_score, semantic_explanation, evidence = _score_semantic(resume, jd)
    experience_score, experience_explanation = _score_experience(resume, jd)
    education_score, education_explanation = _score_education(resume, jd)

    raw_categories = [
        ("skills", "Skills coverage", skills_score, weights.skills, skills_explanation),
        ("semantic", "Semantic similarity", semantic_score, weights.semantic, semantic_explanation),
        ("experience", "Experience relevance", experience_score, weights.experience, experience_explanation),
        ("education", "Education alignment", education_score, weights.education, education_explanation),
    ]

    applicable = [(k, l, s, w, e) for (k, l, s, w, e) in raw_categories if s is not None]
    not_applicable = [(k, l, w, e) for (k, l, s, w, e) in raw_categories if s is None]

    total_applicable_weight = sum(w for (_, _, _, w, _) in applicable)
    calculation_notes: list[str] = []

    categories: list[CategoryScore] = []
    overall = 0.0

    for key, label, score, original_weight, explanation in applicable:
        if total_applicable_weight > 0:
            effective_weight = original_weight / total_applicable_weight
        else:
            effective_weight = 0.0
        overall += score * effective_weight
        categories.append(
            CategoryScore(
                key=key, label=label, score=round(score, 3), weight=round(effective_weight, 3),
                applicable=True, explanation=explanation,
            )
        )

    for key, label, original_weight, explanation in not_applicable:
        categories.append(
            CategoryScore(key=key, label=label, score=0.0, weight=0.0, applicable=False, explanation=explanation)
        )
        calculation_notes.append(
            f"'{label}' could not be evaluated, so its weight was redistributed across the other categories."
        )

    calculation_notes.append(
        "Overall score = 100 x sum(category_score x effective_weight) across applicable categories."
    )
    calculation_notes.append(
        "This is an estimated fit indicator. It is not a hiring probability and does not predict interview or hiring outcomes."
    )

    return AnalysisScoreResult(
        overall_score=round(overall * 100),
        weights=weights,
        categories=categories,
        matched_required=skills_details.get("matched_required", []),
        missing_required=skills_details.get("missing_required", []),
        matched_preferred=skills_details.get("matched_preferred", []),
        missing_preferred=skills_details.get("missing_preferred", []),
        evidence=evidence,
        calculation_notes=calculation_notes,
    )