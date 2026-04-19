# Phase 12 Multi-Agent Persistence

Phase 12 upgrades persistence from a single MVP report table into a foundation that can support future multi-agent simulation runs.

## Existing database baseline

Before this phase, the project stored analysis history only in the `reports` table.

That was enough for the MVP, but not enough for:

- multiple agents per run
- per-agent scorecards
- emotion timelines
- consent records
- exports
- replaying a simulation independently from one saved report blob

## What was added

Database initialization in [backend/app/core/database.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/core/database.py>) now creates these additional tables:

- `media_assets`
- `simulation_runs`
- `run_targets`
- `agent_profiles`
- `agent_runs`
- `emotion_samples`
- `timeline_events`
- `consent_records`
- `report_exports`

## Migration strategy

- the original `reports` table remains in place
- legacy MVP reports are backfilled into:
  - `media_assets`
  - `simulation_runs`
  - `run_targets`
- old report retrieval remains intact because no existing read path was removed

## Why this design was chosen

- it preserves the MVP flow
- it adds normalized tables for future multi-agent work
- it allows a later runtime to store partial progress, per-agent outputs, and timeline signals without forcing everything into one JSON blob

## Current implementation boundary

Phase 12 adds the persistence foundation and migration behavior.

It does not yet populate `agent_runs`, `emotion_samples`, `timeline_events`, or `consent_records` during normal analysis, because the multi-agent runtime has not been implemented yet.
