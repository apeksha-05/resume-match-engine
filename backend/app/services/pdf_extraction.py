import pymupdf

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MIN_EXTRACTED_WORDS = 50  # below this, we assume a scanned or empty PDF
MAX_PAGES = 10
MAX_TEXT_CHARS = 100_000
PDF_MAGIC = b"%PDF-"


class PdfValidationError(Exception):
    """Raised when an uploaded file cannot be used as a resume."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts plain text from a PDF's bytes.

    Raises PdfValidationError if the file is empty, too large, not really a
    PDF, password-protected, too long, damaged, or contains no readable text
    (for example a scanned image without a text layer).
    """
    if len(file_bytes) == 0:
        raise PdfValidationError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise PdfValidationError("The file is too large. Maximum size is 5 MB.")

    # A real PDF carries its header near the start; some generators add a few leading bytes.
    if PDF_MAGIC not in file_bytes[:1024]:
        raise PdfValidationError("This file is not a valid PDF.")

    try:
        document = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfValidationError(
            "This file could not be read as a PDF. It may be corrupted or not a real PDF."
        ) from exc

    try:
        if document.needs_pass:
            raise PdfValidationError(
                "This PDF is password-protected. Please upload an unprotected copy."
            )
        if document.page_count > MAX_PAGES:
            raise PdfValidationError(
                f"This PDF has {document.page_count} pages. "
                f"Resumes longer than {MAX_PAGES} pages are not supported."
            )
        pages_text = [page.get_text() for page in document]
    except PdfValidationError:
        raise
    except Exception as exc:
        raise PdfValidationError("This PDF could not be read. It may be damaged.") from exc
    finally:
        document.close()

    full_text = "\n".join(pages_text).strip()

    if len(full_text.split()) < MIN_EXTRACTED_WORDS:
        raise PdfValidationError(
            "This PDF does not appear to contain readable text. It may be a "
            "scanned image without a text layer. Please upload a text-based PDF."
        )

    return full_text[:MAX_TEXT_CHARS]
