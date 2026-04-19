from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.models.analysis import AnalyzeRequest
from app.models.platforms import SupportedMediaType, TargetPlatform
from app.services.analyzer_service import analyze_media
from app.services.report_service import generate_report_from_analysis


def test_image_analysis_returns_normalized_signals(tmp_path: Path) -> None:
    image_path = tmp_path / "sample-image.png"
    pixels = np.zeros((120, 120, 3), dtype=np.uint8)
    pixels[:, :60] = [240, 180, 40]
    pixels[:, 60:] = [20, 40, 220]
    Image.fromarray(pixels).save(image_path)

    request = AnalyzeRequest(
        platform=TargetPlatform.INSTAGRAM_REELS,
        media_type=SupportedMediaType.IMAGE,
        filename=image_path.name,
        mime_type="image/png",
        file_size_bytes=image_path.stat().st_size,
    )

    result = analyze_media(image_path, request)

    assert result.media_type == SupportedMediaType.IMAGE
    assert result.technical_metadata.width == 120
    assert result.technical_metadata.height == 120
    assert result.brightness_score >= 0
    assert len(result.extracted_frames) == 1
    assert result.transcript.status == "not_applicable"


def test_video_analysis_returns_sampled_frames_and_placeholder_transcript(
    tmp_path: Path,
) -> None:
    video_path = tmp_path / "sample-video.mp4"
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        5.0,
        (64, 64),
    )
    assert writer.isOpened()

    frame_colors = [
        (255, 20, 20),
        (20, 255, 20),
        (20, 20, 255),
        (240, 240, 80),
        (80, 40, 220),
    ]

    for color in frame_colors:
        frame = np.full((64, 64, 3), color, dtype=np.uint8)
        writer.write(frame)
    writer.release()

    request = AnalyzeRequest(
        platform=TargetPlatform.INSTAGRAM_REELS,
        media_type=SupportedMediaType.SHORT_VIDEO,
        filename=video_path.name,
        mime_type="video/mp4",
        file_size_bytes=video_path.stat().st_size,
        duration_seconds=1.0,
    )

    result = analyze_media(video_path, request)

    assert result.media_type == SupportedMediaType.SHORT_VIDEO
    assert result.technical_metadata.sampled_frame_count >= 1
    assert result.transcript.status == "placeholder"
    assert result.scene_change_ratio >= 0
    assert result.pacing_hint in {"slow pacing", "moderate pacing", "fast-cut pacing"}


def test_report_generation_returns_stable_phase_four_shape(tmp_path: Path) -> None:
    image_path = tmp_path / "report-source.png"
    pixels = np.full((80, 80, 3), [210, 90, 40], dtype=np.uint8)
    Image.fromarray(pixels).save(image_path)

    request = AnalyzeRequest(
        platform=TargetPlatform.INSTAGRAM_REELS,
        media_type=SupportedMediaType.IMAGE,
        filename=image_path.name,
        mime_type="image/png",
        file_size_bytes=image_path.stat().st_size,
    )

    analysis = analyze_media(image_path, request)
    report = generate_report_from_analysis(analysis)

    assert report.platform == TargetPlatform.INSTAGRAM_REELS
    assert 0 <= report.hook_score <= 100
    assert 0 <= report.engagement_score <= 100
    assert 0 <= report.boring_rate <= 100
    assert report.peak_moments
    assert report.simulated_comments
    assert report.improvements
