from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.resume import ResumeTextExtractionOut
from app.services.pdf_extraction import PdfValidationError, extract_text_from_pdf

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"application/pdf"}


@router.post("/resumes/extract-text", response_model=ResumeTextExtractionOut)
async def extract_resume_text(file: UploadFile = File(...)) -> ResumeTextExtractionOut:
    """Step 1 of resume processing: validate and extract raw text only.
    Structured extraction (skills, experience, etc.) is added in Phase 5B."""

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()

    try:
        text = extract_text_from_pdf(file_bytes)
    except PdfValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ResumeTextExtractionOut(
        filename=file.filename or "unknown.pdf",
        word_count=len(text.split()),
        preview=text[:500],
    )