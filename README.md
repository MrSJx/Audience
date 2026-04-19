# Audience

Audience is an AI product for simulating how people may react to content before it is posted online.

The project is now aligned around `Meta Llama 3.2 3B` for local report generation.

This repository now includes all 10 phases of the MVP plan from [structure guidelines.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/structure guidelines.md>).

## Current Status

- Phase 1 scaffold completed
- Phase 2 MVP flow documented
- Phase 3 analyzer pipeline added for image and short video
- Phase 4 report schema stabilized with deterministic example output
- Phase 5 API endpoints added, including upload analysis and report retrieval
- Phase 6 frontend MVP now uploads files and renders saved reports
- Phase 7 prompt reliability layer added with structured prompt and parser modules
- Phase 8 SQLite persistence stores generated reports locally
- Phase 9 core flow testing now covers high-value failure and retrieval paths
- Phase 10 product wording, setup guidance, and UI clarity refinements completed
- Phase 11 Simulation 2.0 contract added for future multi-agent runs
- Phase 12 multi-agent persistence foundation added without breaking MVP report history
- Local `Llama 3.2` report generation path added through Ollama

## Project Structure

```text
Audience/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- models/
|   |   |-- services/
|   |   |-- utils/
|   |   `-- main.py
|   |-- tests/
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |-- index.html
|   `-- package.json
|-- docs/
|-- LICENSE
|-- README.md
`-- structure guidelines.md
```

## Backend Quick Start

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
ollama run llama3.2
uvicorn app.main:app --reload
```

Optional backend environment variables:

```bash
AUDIENCE_OLLAMA_BASE_URL=http://127.0.0.1:11434
AUDIENCE_OLLAMA_MODEL=llama3.2
AUDIENCE_USE_HEURISTIC_FALLBACK=false
```

Once running, open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/contract`
- `http://127.0.0.1:8000/report-schema`
- `http://127.0.0.1:8000/simulation-schema`
- `http://127.0.0.1:8000/docs`

## Frontend Quick Start

```bash
cd frontend
npm install
npm run dev
```

The frontend is intentionally minimal in Phase 1 and serves as the starter surface for the future upload and report flow.

The current frontend is now a functional MVP client for the backend upload and report flow.

The multi-agent runtime is not implemented yet, but the Phase 11 contract and Phase 12 persistence foundation are now in place for that next layer of work.

## MVP Contract

Phase 2 locks the first supported product flow:

- platform: `instagram_reels`
- supported media: `image`, `short_video`
- upload mode: one file per request
- response shape: structured audience reaction report

The detailed contract is documented in [docs/phase-2-mvp-flow.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-2-mvp-flow.md>).

## Analyzer And Report Foundation

Phases 3 and 4 add:

- normalized internal media analysis output
- heuristic image and short video signal extraction
- sampled frame analysis for video
- transcript placeholder integration
- stable report schema and example response
- local Llama 3.2 report generation with the same response contract

Supporting docs:

- [docs/phase-3-analyzer.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-3-analyzer.md>)
- [docs/phase-4-report-schema.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-4-report-schema.md>)

## API And Persistence

Phases 5 through 8 add:

- `POST /analyze` for upload-driven analysis
- `GET /report/{id}` for persisted report retrieval
- `GET /reports` for recent report listing
- startup SQLite initialization
- local upload storage under `backend/uploads/`
- local database storage under `backend/data/audience.db`

Supporting docs:

- [docs/phase-5-api.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-5-api.md>)
- [docs/phase-6-frontend.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-6-frontend.md>)
- [docs/phase-7-prompt-reliability.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-7-prompt-reliability.md>)
- [docs/phase-8-persistence.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-8-persistence.md>)

## Testing And Refinement

The final roadmap phases add:

- stronger automated coverage around the real upload-to-report path
- documented known limitations
- clearer user-facing wording and error messages
- improved score framing so the MVP reads as guidance, not certainty

Supporting docs:

- [docs/phase-9-testing.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-9-testing.md>)
- [docs/phase-10-refinement.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-10-refinement.md>)
- [docs/phase-11-simulation-contract.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-11-simulation-contract.md>)
- [docs/phase-12-multi-agent-persistence.md](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/docs/phase-12-multi-agent-persistence.md>)

## Current Outcome

The MVP is locally runnable as a narrow but coherent first version, with report generation aimed at a local Llama 3.2 workflow.

## Notes

- The MVP remains intentionally narrow.
- Phase 1 avoids implementing business logic or media analysis.
- The backend and frontend structure are designed to support later phases without major reshuffling.
