import pymupdf

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MIN_EXTRACTED_WORDS = 50  # below this, we assume a scanned or empty PDF


class PdfValidationError(Exception):
    """Raised when an uploaded file cannot be used as a resume."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts plain text from a PDF's bytes.

    Raises PdfValidationError if the file is too large, not a valid PDF,
    or appears to contain no real text (e.g. a scanned image with no OCR layer).
    """
    if len(file_bytes) == 0:
        raise PdfValidationError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise PdfValidationError("The file is too large. Maximum size is 5 MB.")

    try:
        document = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfValidationError(
            "This file could not be read as a PDF. It may be corrupted or not a real PDF."
        ) from exc

    try:
        pages_text = [page.get_text() for page in document]
    finally:
        document.close()

    full_text = "\n".join(pages_text).strip()
    word_count = len(full_text.split())

    if word_count < MIN_EXTRACTED_WORDS:
        raise PdfValidationError(
            "This PDF does not appear to contain readable text. It may be a "
            "scanned image without a text layer. Please upload a text-based PDF."
        )

    return full_text