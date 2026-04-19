# Audience - Llama 3.2 Direction Report

> **Date:** April 20, 2026  
> **Purpose:** Record the current project direction after moving fully to local `Meta Llama 3.2 3B`.

---

## Current Direction

Audience now targets a local-first report generation workflow built around:

- `Meta Llama 3.2 3B`
- local inference through `Ollama`
- existing FastAPI + React MVP structure
- the current image and short-video analysis pipeline as structured context for the model

This means the product no longer references or depends on the old model direction.

---

## What Changed In The Codebase

- Added a dedicated local LLM integration in `backend/app/services/llm_service.py`
- Updated `report_service.py` so report generation now prefers `Llama 3.2`
- Strengthened `parser_service.py` so it can parse raw JSON or fenced JSON from model output
- Updated prompt instructions in `prompt_service.py` for strict JSON responses
- Added Ollama-related settings in `backend/app/core/config.py`
- Updated backend metadata, frontend copy, and repo docs to reflect the Llama 3.2 plan
- Removed old licensing language that implied the previous model restriction

---

## Current Runtime Behavior

The app now expects a local Ollama setup using:

```bash
ollama run llama3.2
```

If Ollama is unavailable, the backend can still fall back to the older heuristic report builder when `AUDIENCE_USE_HEURISTIC_FALLBACK=true`.

Default LLM-related settings:

```bash
AUDIENCE_OLLAMA_BASE_URL=http://127.0.0.1:11434
AUDIENCE_OLLAMA_MODEL=llama3.2
AUDIENCE_USE_HEURISTIC_FALLBACK=true
```

---

## What Still Remains For The Bigger Vision

The model swap is done at the direction level, but the wider product roadmap still remains:

- richer emotion scoring
- longer and more realistic simulated comments
- demographic breakdowns
- performance prediction bars
- more platforms beyond Instagram Reels
- real speech-to-text instead of the current transcript placeholder

---

## Bottom Line

The codebase is now aligned with a `local Llama 3.2` strategy.

The main MVP architecture did not need a full rewrite. The biggest changes were in:

- report generation
- model configuration
- project documentation
- license/model notes
