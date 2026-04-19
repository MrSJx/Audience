# Phase 7 Prompt Reliability

Phase 7 adds a reliability layer around report generation.

## Implemented modules

- [backend/app/services/prompt_service.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/services/prompt_service.py>)
- [backend/app/services/parser_service.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/services/parser_service.py>)

## Current approach

- build a reusable structured prompt from normalized analysis signals
- require one fixed JSON field set
- validate generated payloads against `AudienceReactionReport`
- target local `Llama 3.2` generation without changing the API contract
- keep a heuristic fallback path available for local development resilience

This keeps the current contract stable while the report generator is driven by a local Llama 3.2 workflow.
