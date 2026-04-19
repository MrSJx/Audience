from __future__ import annotations

from pathlib import Path

import cv2

from app.models.contracts import UploadContract
from app.models.platforms import SupportedMediaType


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".webm"}


def detect_media_type(file_path: str | Path, mime_type: str | None = None) -> SupportedMediaType:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if mime_type:
        normalized = mime_type.lower()
        if normalized.startswith("image/"):
            return SupportedMediaType.IMAGE
        if normalized.startswith("video/"):
            return SupportedMediaType.SHORT_VIDEO

    if suffix in IMAGE_SUFFIXES:
        return SupportedMediaType.IMAGE
    if suffix in VIDEO_SUFFIXES:
        return SupportedMediaType.SHORT_VIDEO

    raise ValueError(f"Unsupported media type for file: {path.name}")


def validate_media_file(
    file_path: str | Path,
    media_type: SupportedMediaType,
    mime_type: str,
    contract: UploadContract | None = None,
) -> Path:
    active_contract = contract or UploadContract()
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file path, got: {path}")

    max_bytes = active_contract.max_file_size_mb * 1024 * 1024
    file_size = path.stat().st_size
    if file_size > max_bytes:
        raise ValueError(
            f"File exceeds the {active_contract.max_file_size_mb} MB limit: {path.name}"
        )

    normalized_mime = mime_type.lower()
    if media_type == SupportedMediaType.IMAGE:
        if normalized_mime not in active_contract.accepted_image_mime_types:
            raise ValueError(f"Unsupported image MIME type: {mime_type}")
    elif normalized_mime not in active_contract.accepted_video_mime_types:
        raise ValueError(f"Unsupported video MIME type: {mime_type}")

    detected = detect_media_type(path, normalized_mime)
    if detected != media_type:
        raise ValueError(
            f"Declared media type {media_type.value} does not match detected type {detected.value}."
        )

    return path


def probe_video_duration_seconds(file_path: str | Path) -> float | None:
    capture = cv2.VideoCapture(str(file_path))
    if not capture.isOpened():
        return None

    try:
        fps = capture.get(cv2.CAP_PROP_FPS) or 0.0
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0
        if fps <= 0 or frame_count <= 0:
            return None
        return round(frame_count / fps, 2)
    finally:
        capture.release()
