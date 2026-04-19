from io import BytesIO

import cv2
import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def _build_image_bytes() -> bytes:
    image = Image.new("RGB", (96, 96), color=(220, 90, 60))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _build_video_bytes(tmp_path) -> bytes:
    video_path = tmp_path / "sample-api-video.mp4"
    writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), 5.0, (64, 64))
    assert writer.isOpened()

    for color in [(255, 20, 20), (20, 255, 20), (20, 20, 255), (250, 220, 30)]:
        writer.write(np.full((64, 64, 3), color, dtype=np.uint8))
    writer.release()

    return video_path.read_bytes()


def test_analyze_endpoint_creates_and_returns_persisted_report() -> None:
    response = client.post(
        "/analyze",
        files={"file": ("sample.png", _build_image_bytes(), "image/png")},
        data={"platform": "instagram_reels", "caption": "A test upload."},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"]
    assert payload["report"]["platform"] == "instagram_reels"
    assert payload["analysis"]["media_type"] == "image"


def test_report_retrieval_returns_saved_report() -> None:
    created = client.post(
        "/analyze",
        files={"file": ("saved.png", _build_image_bytes(), "image/png")},
        data={"platform": "instagram_reels"},
    )
    report_id = created.json()["id"]

    fetched = client.get(f"/report/{report_id}")

    assert fetched.status_code == 200
    assert fetched.json()["id"] == report_id


def test_reports_listing_returns_saved_reports() -> None:
    response = client.get("/reports")

    assert response.status_code == 200
    assert "reports" in response.json()


def test_analyze_video_can_infer_duration_when_omitted(tmp_path) -> None:
    response = client.post(
        "/analyze",
        files={"file": ("sample.mp4", _build_video_bytes(tmp_path), "video/mp4")},
        data={"platform": "instagram_reels"},
    )

    assert response.status_code == 201
    assert response.json()["analysis"]["technical_metadata"]["duration_seconds"] is not None


def test_analyze_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/analyze",
        files={"file": ("notes.txt", b"plain text", "text/plain")},
        data={"platform": "instagram_reels"},
    )

    assert response.status_code == 400
    assert "Unsupported media type" in response.json()["detail"]


def test_analyze_rejects_video_duration_over_limit(tmp_path) -> None:
    response = client.post(
        "/analyze",
        files={"file": ("too-long.mp4", _build_video_bytes(tmp_path), "video/mp4")},
        data={"platform": "instagram_reels", "duration_seconds": "120"},
    )

    assert response.status_code == 400
    assert "less than or equal to 90" in response.json()["detail"]


def test_report_lookup_returns_404_for_missing_id() -> None:
    response = client.get("/report/does-not-exist")

    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]
