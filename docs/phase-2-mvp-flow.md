# Phase 2 MVP Flow

This document defines the first shared contract for Audience so later backend and frontend work can build against the same assumptions.

## First Supported User Flow

1. The user chooses `Instagram Reels`.
2. The user uploads one file.
3. The file must be either an `image` or a `short_video`.
4. The backend validates the upload metadata and media type.
5. The backend extracts signals from the media.
6. The backend produces a structured audience reaction report.
7. The frontend renders the report and the improvement suggestions.

## User Input Contract

The MVP request contract is represented in code by `AnalyzeRequest`.

### Required fields

- `platform`
- `media_type`
- `filename`
- `mime_type`
- `file_size_bytes`

### Conditional field

- `duration_seconds`
  - required for `short_video`
  - omitted for `image`

### Optional field

- `caption`

## Response Contract

The MVP response contract is represented in code by `AudienceReactionReport`.

Fields:

- `platform`
- `content_summary`
- `hook_score`
- `engagement_score`
- `boring_rate`
- `peak_moments`
- `simulated_comments`
- `final_verdict`
- `improvements`

## Supported Platform Behavior

Only one platform is supported in the MVP:

- `instagram_reels`

This keeps the first end-to-end path narrow and avoids premature expansion into platform-specific branching.

## Upload Rules

The current upload contract is represented in code by `UploadContract`.

Current MVP rules:

- one file per analysis request
- supported media types: `image`, `short_video`
- accepted image MIME types: `image/jpeg`, `image/png`, `image/webp`
- accepted video MIME types: `video/mp4`, `video/quicktime`, `video/webm`
- file size limit: `100 MB`
- short video duration limit: `90 seconds`

## Error Cases To Expect

- unsupported platform
- unsupported media type
- missing `duration_seconds` for video
- `duration_seconds` provided for image
- invalid MIME type
- empty filename
- file too large
- video duration over the MVP limit

## Why This Phase Matters

Phase 2 removes ambiguity. Frontend work, analyzer work, and API work can now target one shared request and response shape instead of inventing separate assumptions.
