from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.models.analysis import (
    AnalyzeRequest,
    FrameSignal,
    MediaAnalysisResult,
    MediaTechnicalMetadata,
)
from app.models.platforms import SupportedMediaType
from app.services.transcript_service import extract_transcript_placeholder
from app.utils.media import validate_media_file


_FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_FACE_CASCADE = cv2.CascadeClassifier(_FACE_CASCADE_PATH)


def analyze_media(file_path: str | Path, request: AnalyzeRequest) -> MediaAnalysisResult:
    validated_path = validate_media_file(file_path, request.media_type, request.mime_type)

    if request.media_type == SupportedMediaType.IMAGE:
        return _analyze_image(validated_path, request)

    return _analyze_video(validated_path, request)


def _analyze_image(file_path: Path, request: AnalyzeRequest) -> MediaAnalysisResult:
    with Image.open(file_path) as image:
        rgb_image = image.convert("RGB")
        width, height = rgb_image.size
        frame = np.array(rgb_image)

    brightness, contrast, saturation = _frame_metrics(frame)
    text_present = _estimate_text_presence(frame)
    face_count = _detect_faces(frame)
    summary_cues = _build_image_cues(brightness, contrast, saturation, text_present, face_count)

    return MediaAnalysisResult(
        platform=request.platform,
        media_type=request.media_type,
        filename=request.filename,
        mime_type=request.mime_type,
        file_size_bytes=request.file_size_bytes,
        technical_metadata=MediaTechnicalMetadata(
            width=width,
            height=height,
            duration_seconds=None,
            fps=None,
            frame_count=1,
            sampled_frame_count=1,
            audio_present=None,
        ),
        brightness_score=brightness,
        contrast_score=contrast,
        saturation_score=saturation,
        detected_faces=face_count,
        detected_text_present=text_present,
        pacing_hint="static visual",
        transcript=extract_transcript_placeholder(request.media_type),
        extracted_frames=[
            FrameSignal(timestamp="0:00", brightness_score=brightness, contrast_score=contrast)
        ],
        scene_change_ratio=0.0,
        summary_cues=summary_cues,
    )


def _analyze_video(file_path: Path, request: AnalyzeRequest) -> MediaAnalysisResult:
    capture = cv2.VideoCapture(str(file_path))
    if not capture.isOpened():
        raise ValueError(f"Unable to open video file: {file_path.name}")

    try:
        fps = capture.get(cv2.CAP_PROP_FPS) or 0.0
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration_seconds = request.duration_seconds
        if duration_seconds is None and fps > 0 and frame_count > 0:
            duration_seconds = frame_count / fps

        if duration_seconds is not None and duration_seconds > 90:
            raise ValueError("Short video uploads must be 90 seconds or less.")

        sample_indices = _build_sample_indices(frame_count)
        sampled_frames: list[np.ndarray] = []
        extracted_frames: list[FrameSignal] = []
        width = None
        height = None

        for index in sample_indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            success, frame = capture.read()
            if not success:
                continue

            if width is None or height is None:
                height, width = frame.shape[:2]

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            sampled_frames.append(rgb_frame)

            brightness, contrast, _ = _frame_metrics(rgb_frame)
            timestamp_seconds = index / fps if fps > 0 else 0.0
            extracted_frames.append(
                FrameSignal(
                    timestamp=_format_timestamp(timestamp_seconds),
                    brightness_score=brightness,
                    contrast_score=contrast,
                )
            )

        if not sampled_frames:
            raise ValueError(f"No frames could be sampled from video: {file_path.name}")

        brightness_values: list[int] = []
        contrast_values: list[int] = []
        saturation_values: list[int] = []
        face_counts: list[int] = []
        text_flags: list[bool] = []

        for frame in sampled_frames:
            brightness, contrast, saturation = _frame_metrics(frame)
            brightness_values.append(brightness)
            contrast_values.append(contrast)
            saturation_values.append(saturation)
            face_counts.append(_detect_faces(frame))
            text_flags.append(_estimate_text_presence(frame))

        scene_change_ratio = _estimate_scene_change_ratio(sampled_frames)
        pacing_hint = _estimate_pacing_hint(scene_change_ratio)
        summary_cues = _build_video_cues(
            int(round(sum(brightness_values) / len(brightness_values))),
            int(round(sum(contrast_values) / len(contrast_values))),
            int(round(sum(saturation_values) / len(saturation_values))),
            any(text_flags),
            max(face_counts) if face_counts else 0,
            scene_change_ratio,
        )

        return MediaAnalysisResult(
            platform=request.platform,
            media_type=request.media_type,
            filename=request.filename,
            mime_type=request.mime_type,
            file_size_bytes=request.file_size_bytes,
            technical_metadata=MediaTechnicalMetadata(
                width=width,
                height=height,
                duration_seconds=duration_seconds,
                fps=fps if fps > 0 else None,
                frame_count=frame_count if frame_count > 0 else None,
                sampled_frame_count=len(sampled_frames),
                audio_present=None,
            ),
            brightness_score=int(round(sum(brightness_values) / len(brightness_values))),
            contrast_score=int(round(sum(contrast_values) / len(contrast_values))),
            saturation_score=int(round(sum(saturation_values) / len(saturation_values))),
            detected_faces=max(face_counts) if face_counts else 0,
            detected_text_present=any(text_flags),
            pacing_hint=pacing_hint,
            transcript=extract_transcript_placeholder(request.media_type),
            extracted_frames=extracted_frames,
            scene_change_ratio=scene_change_ratio,
            summary_cues=summary_cues,
        )
    finally:
        capture.release()


def _frame_metrics(frame: np.ndarray) -> tuple[int, int, int]:
    rgb_frame = frame.astype(np.uint8)
    gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2HSV)

    brightness = int(round(float(np.mean(gray)) / 255 * 100))
    contrast = int(round(min(float(np.std(gray)) / 64 * 100, 100)))
    saturation = int(round(float(np.mean(hsv[:, :, 1])) / 255 * 100))
    return brightness, contrast, saturation


def _estimate_text_presence(frame: np.ndarray) -> bool:
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float(np.count_nonzero(edges)) / float(edges.size)
    return edge_density > 0.12


def _detect_faces(frame: np.ndarray) -> int:
    if _FACE_CASCADE.empty():
        return 0

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = _FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))
    return int(len(faces))


def _build_sample_indices(frame_count: int) -> list[int]:
    if frame_count <= 0:
        return [0]

    sample_count = min(5, frame_count)
    return sorted({int(round(index)) for index in np.linspace(0, frame_count - 1, sample_count)})


def _estimate_scene_change_ratio(frames: list[np.ndarray]) -> float:
    if len(frames) < 2:
        return 0.0

    scene_changes = 0
    comparisons = 0
    previous_gray = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)

    for frame in frames[1:]:
        current_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        difference = float(np.mean(cv2.absdiff(previous_gray, current_gray)))
        if difference > 28:
            scene_changes += 1
        comparisons += 1
        previous_gray = current_gray

    if comparisons == 0:
        return 0.0

    return round(scene_changes / comparisons, 2)


def _estimate_pacing_hint(scene_change_ratio: float) -> str:
    if scene_change_ratio >= 0.65:
        return "fast-cut pacing"
    if scene_change_ratio >= 0.3:
        return "moderate pacing"
    return "slow pacing"


def _build_image_cues(
    brightness: int,
    contrast: int,
    saturation: int,
    text_present: bool,
    face_count: int,
) -> list[str]:
    cues = [_brightness_cue(brightness), _contrast_cue(contrast), _color_cue(saturation)]
    if text_present:
        cues.append("possible text overlay or dense graphic detail")
    if face_count > 0:
        cues.append(f"{face_count} likely face area(s) detected")
    return cues


def _build_video_cues(
    brightness: int,
    contrast: int,
    saturation: int,
    text_present: bool,
    face_count: int,
    scene_change_ratio: float,
) -> list[str]:
    cues = [_brightness_cue(brightness), _contrast_cue(contrast), _color_cue(saturation)]
    cues.append(f"scene change ratio around {scene_change_ratio:.2f}")
    if text_present:
        cues.append("possible on-screen text or high-detail frames")
    if face_count > 0:
        cues.append("at least one likely face detected in sampled frames")
    return cues


def _brightness_cue(brightness: int) -> str:
    if brightness >= 70:
        return "bright overall visual tone"
    if brightness <= 35:
        return "dark overall visual tone"
    return "balanced brightness"


def _contrast_cue(contrast: int) -> str:
    if contrast >= 65:
        return "high visual contrast"
    if contrast <= 30:
        return "soft visual contrast"
    return "moderate visual contrast"


def _color_cue(saturation: int) -> str:
    if saturation >= 65:
        return "vivid color intensity"
    if saturation <= 30:
        return "muted color intensity"
    return "moderate color intensity"


def _format_timestamp(seconds: float) -> str:
    whole_seconds = max(int(round(seconds)), 0)
    minutes, remaining_seconds = divmod(whole_seconds, 60)
    return f"{minutes}:{remaining_seconds:02d}"
