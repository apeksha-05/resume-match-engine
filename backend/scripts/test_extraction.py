"""Manual test script for resume extraction (mock or real, based on config).
Run with: python -m scripts.test_extraction path\\to\\resume.pdf
"""

import sys

from app.core.config import get_settings
from app.services.evidence_verification import filter_unverified_skills
from app.services.pdf_extraction import extract_text_from_pdf
from app.services.resume_extraction import extract_structured_resume
from app.services.text_cleanup import clean_extracted_text


def run(pdf_path: str) -> None:
    settings = get_settings()
    mode = "MOCK (keyword matching)" if settings.use_mock_llm else "REAL (Gemini API)"
    print(f"Extraction mode: {mode}\n")

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    raw_text = extract_text_from_pdf(file_bytes)
    cleaned_text = clean_extracted_text(raw_text)

    print(f"Extracted {len(cleaned_text.split())} words. Running extraction...\n")

    parsed = extract_structured_resume(cleaned_text)
    parsed = filter_unverified_skills(parsed, cleaned_text)

    print(parsed.model_dump_json(indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.test_extraction path\\to\\resume.pdf")
        sys.exit(1)
    run(sys.argv[1])