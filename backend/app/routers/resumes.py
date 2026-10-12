import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id, require_existing_user
from app.core.database import get_db
from app.core.limits import limit_uploads
from app.models.resume import Resume
from app.schemas.resume import ResumeOut, ResumeSummaryOut
from app.services.evidence_verification import filter_unverified_skills
from app.services.pdf_extraction import (
    MAX_FILE_SIZE_BYTES,
    PdfValidationError,
    extract_text_from_pdf,
)
from app.services.prompt_safety import looks_like_prompt_injection
from app.services.resume_extraction import ResumeExtractionError, extract_structured_resume
from app.services.resume_summary import to_resume_summary
from app.services.text_cleanup import clean_extracted_text
from app.services.uploads import read_upload_limited, safe_filename

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

ALLOWED_CONTENT_TYPES = {"application/pdf"}


@router.post(
    "/resumes",
    response_model=ResumeOut,
    status_code=201,
    dependencies=[Depends(limit_uploads), Depends(require_existing_user)],
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ResumeOut:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await read_upload_limited(file, MAX_FILE_SIZE_BYTES)

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except PdfValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    cleaned_text = clean_extracted_text(raw_text)

    if looks_like_prompt_injection(cleaned_text):
        # Log the fact only, never the text. The resume is still processed as plain data.
        logger.warning(
            "An uploaded resume contains text that looks like instructions to an AI system. "
            "It is treated as data only."
        )

    try:
        parsed = extract_structured_resume(cleaned_text)
    except ResumeExtractionError as exc:
        raise HTTPException(
            status_code=502,
            detail="The resume could not be analyzed right now. Please try again.",
        ) from exc
    parsed = filter_unverified_skills(parsed, cleaned_text)

    resume = Resume(
        user_id=user_id,
        filename=safe_filename(file.filename),
        parsed=parsed.model_dump(mode="json"),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeOut.model_validate(
        {
            "id": resume.id,
            "filename": resume.filename,
            "parsed": parsed,
            "created_at": resume.created_at,
        }
    )


@router.get("/resumes", response_model=list[ResumeSummaryOut])
def list_resumes(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ResumeSummaryOut]:
    stmt = (
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).scalars().all()
    return [to_resume_summary(row) for row in rows]


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ResumeOut:
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != user_id:
        raise HTTPException(status_code=404, detail="Resume not found")

    return ResumeOut.model_validate(
        {
            "id": resume.id,
            "filename": resume.filename,
            "parsed": resume.parsed,
            "created_at": resume.created_at,
        }
    )


@router.delete("/resumes/{resume_id}", status_code=204)
def delete_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != user_id:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()