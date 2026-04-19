# Phase 3 Analyzer

Phase 3 adds the first internal analysis pipeline for supported MVP media.

## Scope Implemented

- file ingestion validation
- media type detection
- image signal extraction
- short video signal extraction
- video frame sampling
- transcript extraction hook placeholder
- normalized analysis output

## Current Analyzer Design

The analyzer is implemented in [backend/app/services/analyzer_service.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/services/analyzer_service.py>).

Supported internal flow:

1. Validate the file path, MIME type, and size rules.
2. Detect whether the file is an `image` or `short_video`.
3. Extract normalized signals.
4. Return a `MediaAnalysisResult`.

## Signals Returned

### Image signals

- width and height
- brightness score
- contrast score
- saturation score
- estimated face count
- heuristic text presence
- summary cues

### Video signals

- width and height
- fps
- frame count
- sampled frame count
- duration
- average brightness, contrast, saturation
- estimated face count from sampled frames
- heuristic text presence
- scene change ratio
- pacing hint
- transcript placeholder

## Notes

- The analyzer uses heuristic methods suitable for an MVP.
- Transcript extraction is represented by a stable placeholder contract for now.
- The output shape is normalized so later report generation and API work do not need to parse media-specific internals directly.
