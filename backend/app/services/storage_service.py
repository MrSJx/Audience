from __future__ import annotations

from pathlib import Path, PurePosixPath
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


_SAFE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".webm"}


def persist_upload(upload: UploadFile) -> Path:
    """Save the uploaded file to disk with a randomized name.

    The original filename is never used as part of the stored path.
    Only whitelisted extensions are preserved; anything else is
    stripped to prevent path traversal or extension-based attacks.
    """
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)

    # Use PurePosixPath to neutralize any backslash / traversal tricks
    raw_name = PurePosixPath(upload.filename or "").name
    suffix = Path(raw_name).suffix.lower()
    if suffix not in _SAFE_EXTENSIONS:
        suffix = ""

    stored_name = f"{uuid4().hex}{suffix}"
    destination = settings.uploads_dir / stored_name

    with destination.open("wb") as output:
        while chunk := upload.file.read(1024 * 1024):
            output.write(chunk)

    upload.file.seek(0)
    return destination
