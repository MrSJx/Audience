# Phase 5 API First

Phase 5 exposes the current analyzer and report pipeline through a real backend API.

## Implemented Endpoints

- `GET /health`
- `GET /contract`
- `GET /report-schema`
- `POST /analyze`
- `GET /report/{id}`
- `GET /reports`

## Analyze Flow

`POST /analyze` accepts one uploaded file plus form metadata:

- `file`
- `platform`
- `caption`
- `duration_seconds` for short videos when needed

The endpoint:

1. stores the upload locally
2. validates the file
3. analyzes media signals
4. generates a structured report using local Llama 3.2 when available
5. stores the result in SQLite
6. returns the persisted report payload
