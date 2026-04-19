from app.models.analysis import TranscriptAnalysis
from app.models.platforms import SupportedMediaType


def extract_transcript_placeholder(media_type: SupportedMediaType) -> TranscriptAnalysis:
    if media_type == SupportedMediaType.IMAGE:
        return TranscriptAnalysis(
            status="not_applicable",
            transcript_text=None,
            notes="Transcript extraction does not apply to image uploads.",
        )

    return TranscriptAnalysis(
        status="placeholder",
        transcript_text=None,
        notes=(
            "Transcript extraction hook is reserved for a future Whisper-style "
            "integration. Phase 3 returns a stable placeholder instead."
        ),
    )
