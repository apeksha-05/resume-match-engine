"""Converts between an AnalysisFullResult and the columns of the analyses table.
Kept free of database imports on purpose, so it can be tested without a database.
"""

from typing import Any

from app.schemas.analysis_records import AnalysisDetailOut, AnalysisHistoryItem
from app.schemas.feedback import AnalysisFullResult

_RESULT_KEYS = (
    "matched_required",
    "missing_required",
    "matched_preferred",
    "missing_preferred",
    "evidence",
    "calculation_notes",
)


def short_title(text: str, max_len: int = 80) -> str:
    """Builds a short display title from pasted job description text:
    the first sentence, truncated if needed."""
    first_sentence = text.strip().split(". ", 1)[0].strip()
    if not first_sentence:
        return "Untitled role"
    if len(first_sentence) <= max_len:
        return first_sentence
    return first_sentence[: max_len - 3].rstrip() + "..."


def pack_analysis(
    full: AnalysisFullResult, job_title: str, company: str, is_demo: bool
) -> dict[str, Any]:
    """Returns the column values to store for the Analysis table."""
    dump = full.model_dump(mode="json")
    result = {key: dump[key] for key in _RESULT_KEYS}
    result.update({"job_title": job_title, "company": company, "is_demo": is_demo})
    return {
        "weights": dump["weights"],
        "overall_score": float(full.overall_score),
        "category_scores": {"items": dump["categories"]},
        "result": result,
        "suggestions": {"suggestions": dump["suggestions"], "roadmap": dump["roadmap"]},
    }


def unpack_analysis(row: Any) -> AnalysisDetailOut:
    """Rebuilds the full API response from a stored Analysis row."""
    result = row.result
    return AnalysisDetailOut(
        id=row.id,
        job_title=result["job_title"],
        company=result["company"],
        is_demo=result["is_demo"],
        created_at=row.created_at,
        overall_score=round(row.overall_score),
        weights=row.weights,
        categories=row.category_scores["items"],
        matched_required=result["matched_required"],
        missing_required=result["missing_required"],
        matched_preferred=result["matched_preferred"],
        missing_preferred=result["missing_preferred"],
        evidence=result["evidence"],
        calculation_notes=result["calculation_notes"],
        suggestions=row.suggestions["suggestions"],
        roadmap=row.suggestions["roadmap"],
    )


def to_history_item(row: Any) -> AnalysisHistoryItem:
    result = row.result or {}
    return AnalysisHistoryItem(
        id=row.id,
        job_title=result.get("job_title", "Untitled role"),
        company=result.get("company", ""),
        overall_score=round(row.overall_score),
        created_at=row.created_at,
    )