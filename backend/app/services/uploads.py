import re

from fastapi import HTTPException, UploadFile

CHUNK_SIZE_BYTES = 64 * 1024
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")


async def read_upload_limited(file: UploadFile, max_bytes: int) -> bytes:
    """Reads an upload in chunks and stops as soon as it exceeds max_bytes,
    instead of loading an arbitrarily large file into memory first."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"The file is too large. Maximum size is {max_bytes // (1024 * 1024)} MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


def safe_filename(raw: str | None, default: str = "resume.pdf", max_length: int = 120) -> str:
    """Makes a client-supplied filename safe to store and display: removes any
    folder path and control characters, and shortens it while keeping the extension."""
    if not raw:
        return default

    name = raw.replace("\\", "/").split("/")[-1]
    name = _CONTROL_CHARACTERS.sub("", name).strip()
    if not name or name in {".", ".."}:
        return default

    if len(name) > max_length:
        base, dot, extension = name.rpartition(".")
        if dot and 0 < len(extension) <= 10:
            name = base[: max_length - len(extension) - 1] + "." + extension
        else:
            name = name[:max_length]
    return name