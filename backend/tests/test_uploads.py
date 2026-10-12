import asyncio
import io

import pytest
from fastapi import HTTPException, UploadFile

from app.services.uploads import read_upload_limited, safe_filename


def make_upload(data: bytes) -> UploadFile:
    return UploadFile(file=io.BytesIO(data), filename="resume.pdf")


def test_normal_name_is_unchanged():
    assert safe_filename("My Resume (final).pdf") == "My Resume (final).pdf"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("C:\\Users\\Ram\\Downloads\\cv.pdf", "cv.pdf"),
        ("../../etc/passwd", "passwd"),
        ("/tmp/uploads/resume.pdf", "resume.pdf"),
    ],
)
def test_folder_paths_are_removed(raw: str, expected: str):
    assert safe_filename(raw) == expected


def test_control_characters_are_removed():
    assert safe_filename("my\x00res\nume.pdf") == "myresume.pdf"


@pytest.mark.parametrize("raw", [None, "", "   ", ".."])
def test_empty_or_missing_names_use_the_default(raw):
    assert safe_filename(raw) == "resume.pdf"


def test_long_names_are_shortened_but_keep_the_extension():
    result = safe_filename("a" * 300 + ".pdf")

    assert len(result) <= 120
    assert result.endswith(".pdf")


def test_reads_a_small_upload():
    data = b"a" * 1000

    assert asyncio.run(read_upload_limited(make_upload(data), max_bytes=5000)) == data


def test_rejects_an_upload_over_the_limit():
    with pytest.raises(HTTPException) as error:
        asyncio.run(read_upload_limited(make_upload(b"a" * 2000), max_bytes=1000))

    assert error.value.status_code == 413


def test_reads_an_empty_upload():
    assert asyncio.run(read_upload_limited(make_upload(b""), max_bytes=1000)) == b""