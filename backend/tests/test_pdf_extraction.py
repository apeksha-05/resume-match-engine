import pymupdf
import pytest

from app.services.pdf_extraction import (
    MAX_FILE_SIZE_BYTES,
    PdfValidationError,
    extract_text_from_pdf,
)


def make_pdf(text: str | None) -> bytes:
    """Builds a one-page PDF in memory. text=None gives a blank page, like a
    scanned image with no text layer."""
    document = pymupdf.open()
    page = document.new_page()
    if text:
        page.insert_textbox(pymupdf.Rect(50, 50, 550, 780), text, fontsize=10)
    data = document.tobytes()
    document.close()
    return data


def test_extracts_text_from_a_normal_pdf():
    words = " ".join(f"skill{i}" for i in range(60))

    text = extract_text_from_pdf(make_pdf(words))

    assert "skill0" in text
    assert "skill59" in text
    assert len(text.split()) >= 60


def test_rejects_a_pdf_with_no_text_layer():
    with pytest.raises(PdfValidationError, match="readable text"):
        extract_text_from_pdf(make_pdf(None))


def test_rejects_a_pdf_with_only_a_few_words():
    with pytest.raises(PdfValidationError, match="readable text"):
        extract_text_from_pdf(make_pdf("just a few words here"))


def test_rejects_an_empty_file():
    with pytest.raises(PdfValidationError, match="empty"):
        extract_text_from_pdf(b"")


def test_rejects_an_oversized_file():
    with pytest.raises(PdfValidationError, match="too large"):
        extract_text_from_pdf(b"0" * (MAX_FILE_SIZE_BYTES + 1))


def test_rejects_data_that_is_not_a_pdf():
    with pytest.raises(PdfValidationError):
        extract_text_from_pdf(b"this is definitely not a pdf file")