import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models.analysis import AnalyzeRequest
from app.models.platforms import SupportedMediaType, TargetPlatform


client = TestClient(app)


def test_contract_endpoint_returns_phase_two_shapes() -> None:
    response = client.get("/contract")

    assert response.status_code == 200

    payload = response.json()
    assert payload["first_user_flow"]["supported_platform"] == "instagram_reels"
    assert "request_example" in payload
    assert "response_example" in payload
    assert payload["upload_contract"]["upload_mode"] == "single_file"


def test_analyze_request_accepts_valid_image_payload() -> None:
    request = AnalyzeRequest(
        platform=TargetPlatform.INSTAGRAM_REELS,
        media_type=SupportedMediaType.IMAGE,
        filename="cover.png",
        mime_type="image/png",
        file_size_bytes=2048,
        caption="Fast visual hook.",
    )

    assert request.duration_seconds is None


def test_analyze_request_requires_duration_for_short_video() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            platform=TargetPlatform.INSTAGRAM_REELS,
            media_type=SupportedMediaType.SHORT_VIDEO,
            filename="clip.mp4",
            mime_type="video/mp4",
            file_size_bytes=4096,
        )
