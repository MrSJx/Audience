# Phase 4 Report Schema

Phase 4 stabilizes the report shape that later frontend and API work will depend on.

## Stable Report Model

The report schema is represented by `AudienceReactionReport` in [backend/app/models/analysis.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/models/analysis.py>).

Stable fields:

- `platform`
- `content_summary`
- `hook_score`
- `engagement_score`
- `boring_rate`
- `peak_moments`
- `simulated_comments`
- `final_verdict`
- `improvements`

## Why It Is Stable

- field names are short and durable
- all score fields are bounded from `0` to `100`
- peak moments use a consistent timestamp and event structure
- the response shape is ready for frontend rendering

## Example Output

The backend exposes a reference snapshot at `GET /report-schema`.

The report layer also includes a deterministic MVP generator in [backend/app/services/report_service.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/services/report_service.py>) so example output can be produced consistently from normalized analysis signals.
