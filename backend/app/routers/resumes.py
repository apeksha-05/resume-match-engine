import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dev_auth import get_current_user_id
from app.models.resume import Resume
from app.schemas.resume import ResumeOut
from app.services.evidence_verification import filter_unverified_skills
from app.services.pdf_extraction import PdfValidationError, extract_text_from_pdf
from app.services.resume_extraction import extract_structured_resume
from app.services.text_cleanup import clean_extracted_text

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"application/pdf"}


@router.post("/resumes", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ResumeOut:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except PdfValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    cleaned_text = clean_extracted_text(raw_text)
    parsed = extract_structured_resume(cleaned_text)
    parsed = filter_unverified_skills(parsed, cleaned_text)

    resume = Resume(
        user_id=user_id,
        filename=file.filename or "unknown.pdf",
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