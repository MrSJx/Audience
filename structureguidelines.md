# Structure Guidelines

This document is the execution guide for building **Audience** from concept to MVP. It is written so future work can be requested phase-by-phase with commands like:

- "Complete Phase 1"
- "Start Phase 3"
- "Do Phase 5"

When a phase is requested, execution should follow the scope, deliverables, and rules in this file unless the user explicitly changes them.

---

## Project Intent

**Audience** is an AI product for simulating how people may react to content before it is posted online.

Initial product direction:

- Accept creator content before publishing
- Analyze likely audience response
- Tailor feedback to a target platform
- Produce an honest, structured reaction report
- Help creators improve hook, pacing, emotional impact, and shareability

---

## MVP Product Boundary

To keep the first working version realistic, the MVP should be intentionally narrow.

### In Scope

- One backend service
- One minimal frontend
- One primary target platform: `Instagram Reels`
- One initial report pipeline
- Support for `image` and `short video`
- Structured response with audience-style feedback

### Out of Scope For MVP

- Multi-platform benchmarking
- Complex demographic modeling
- True predictive virality claims
- Large-scale analytics dashboards
- Full social API integrations
- User auth and billing
- Production deployment hardening

---

## Default Technical Direction

Unless the user explicitly changes course, future implementation should assume:

- Backend: `Python`
- API framework: `FastAPI`
- Frontend: minimal `React` app or simple HTML frontend, depending on repo maturity
- Media processing: `OpenCV`, `ffmpeg`, `moviepy`
- Speech-to-text: `Whisper` or equivalent
- Storage: `SQLite` for MVP
- Data format: structured `JSON`

If constraints appear later, these defaults may be adapted, but only when there is a clear benefit.

---

## Working Principles

These rules should guide all future phase execution:

1. Keep the MVP narrow and shippable.
2. Prefer working software over ambitious architecture.
3. Build API-first so the frontend does not block progress.
4. Lock schemas early to avoid constant rewrites.
5. Use clean modules so future phases can extend safely.
6. Add tests for the core path as early as practical.
7. Avoid adding speculative features before the current phase is stable.

---

## Canonical MVP Flow

The first end-to-end user flow should be:

1. User uploads media
2. User selects the target platform
3. Backend extracts media signals
4. Backend sends structured analysis context to an LLM or rule-based generator
5. System returns an Audience Reaction Report
6. Frontend displays the report clearly

This flow is the backbone of the project. Future phases should strengthen it before expanding scope.

---

## Standard Report Shape

Unless intentionally revised later, MVP output should include:

- `platform`
- `content_summary`
- `hook_score`
- `engagement_score`
- `boring_rate`
- `peak_moments`
- `simulated_comments`
- `final_verdict`
- `improvements`

Suggested JSON shape:

```json
{
  "platform": "instagram_reels",
  "content_summary": "A short comedic reel with a strong visual opener and slower middle section.",
  "hook_score": 74,
  "engagement_score": 68,
  "boring_rate": 29,
  "peak_moments": [
    {
      "timestamp": "0:03",
      "event": "strong visual hook"
    },
    {
      "timestamp": "0:11",
      "event": "pacing slows"
    }
  ],
  "simulated_comments": [
    "The first few seconds grabbed me immediately.",
    "The middle felt a little slower than the intro."
  ],
  "final_verdict": "Strong opening and good concept, but pacing refinement could improve retention.",
  "improvements": [
    "Tighten the middle section.",
    "Bring the strongest beat earlier."
  ]
}
```

This schema should be treated as the contract between backend and frontend during early development.

---

## Recommended Repository Structure

Target structure for the initial implementation:

```text
Audience/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
├── samples/
├── .gitignore
├── LICENSE
├── README.md
└── structure guidelines.md
```

### Backend Module Intent

- `api/`: routes and request handling
- `core/`: config, settings, app bootstrap concerns
- `models/`: request and response schemas
- `services/`: analysis pipeline and report generation
- `utils/`: file handling, parsing, helper utilities

### Frontend Module Intent

- upload flow
- platform selection
- loading state
- report rendering

---

## Phase 1: Create The Basic Structure

### Objective

Turn the repo from concept-only into a real starter codebase with folders, starter files, and a clean foundation.

### Scope

- Create backend directory structure
- Create frontend directory structure
- Create docs directory
- Add starter dependency files
- Add starter app entrypoints
- Add placeholder README notes where useful

### Deliverables

- `backend/`
- `backend/app/`
- `backend/app/api/`
- `backend/app/core/`
- `backend/app/models/`
- `backend/app/services/`
- `backend/app/utils/`
- `backend/tests/`
- `backend/requirements.txt`
- `backend/app/main.py`
- `frontend/`
- `frontend/src/`
- `docs/`
- optional placeholder files such as `.gitkeep`, starter `README.md`, or minimal config files

### Minimum Completion Standard

Phase 1 is complete when:

- the repository contains the core folders
- backend has a runnable starting point
- frontend has a visible starting point or scaffold placeholder
- file layout matches the intended MVP direction

### Notes For Execution

- Keep this phase lightweight
- Do not overbuild business logic yet
- Focus on clean scaffolding and naming

---

## Phase 2: Define The First User Flow

### Objective

Translate the product idea into one clear, buildable interaction.

### Scope

- define the exact MVP user journey
- define what the user inputs
- define what the backend returns
- define the first supported platform behavior
- define validation and error cases

### Deliverables

- documented user flow
- request schema
- response schema
- platform enum or constants
- basic upload contract

### Minimum Completion Standard

Phase 2 is complete when:

- there is no ambiguity about the first supported use case
- backend and frontend can be built against the same contract

### Notes For Execution

- default to `Instagram Reels`
- support `image` and `short video`
- avoid premature expansion to many platforms

---

## Phase 3: Build A Simple Analyzer

### Objective

Create the first analysis pipeline that extracts useful signals from uploaded content.

### Scope

- image analysis basics
- video analysis basics
- media metadata extraction
- frame extraction for video
- transcript extraction if speech exists

### Deliverables

- file ingestion logic
- media type detection
- image signal extraction
- video signal extraction
- transcript extraction hook or placeholder integration
- normalized analysis output for report generation

### Suggested Signals

For images:

- brightness
- contrast
- saturation or color intensity
- detected faces
- detected text
- rough subject/object cues

For video:

- duration
- extracted frames at intervals
- scene pacing hints
- transcript text
- basic audio presence

### Minimum Completion Standard

Phase 3 is complete when:

- uploaded media can be parsed
- useful analysis signals are returned in a structured internal format
- the analyzer does not crash on normal supported files

### Notes For Execution

- heuristic extraction is acceptable for MVP
- do not wait for advanced ML before shipping this phase

---

## Phase 4: Design The Report Schema

### Objective

Lock the response shape the application will return to users.

### Scope

- define the report model
- define score fields
- define peak moments format
- define simulated comments format
- define improvement suggestions format

### Deliverables

- backend report schema models
- sample JSON responses
- schema validation rules
- optional docs describing each field

### Minimum Completion Standard

Phase 4 is complete when:

- the report response is stable enough for frontend work
- example output can be generated consistently

### Notes For Execution

- keep field names simple and durable
- avoid redesigning the schema casually after this phase

---

## Phase 5: Ship API First

### Objective

Build the backend API so the project becomes testable end-to-end before the frontend is polished.

### Scope

- health endpoint
- analyze endpoint
- report retrieval endpoint if persistence exists
- request validation
- error handling

### Deliverables

- `GET /health`
- `POST /analyze`
- optional `GET /report/{id}`
- OpenAPI docs via FastAPI
- validated request and response models

### Minimum Completion Standard

Phase 5 is complete when:

- a user can submit supported media to the API
- the API returns a structured reaction report
- the service runs locally without manual patchwork

### Notes For Execution

- API quality matters more than frontend polish at this stage
- prioritize a clean local developer experience

---

## Phase 6: Add A Minimal Frontend

### Objective

Create a minimal interface that makes the MVP demoable by a normal user.

### Scope

- upload UI
- platform selector
- analyze button
- loading state
- report display

### Deliverables

- frontend app scaffold
- upload form
- API integration
- report page or report component
- error display for unsupported files or failed analysis

### Minimum Completion Standard

Phase 6 is complete when:

- a user can upload a supported file in the browser
- the frontend calls the backend successfully
- the report is rendered in a readable way

### Notes For Execution

- keep styling simple unless the user asks for a more designed interface
- functionality first, appearance second

---

## Phase 7: Make Prompts Reliable

### Objective

Improve consistency and quality of generated audience reports.

### Scope

- create reusable prompt templates
- inject structured media signals
- force reliable output formatting
- reduce hallucinated or inconsistent fields

### Deliverables

- prompt template file or module
- structured prompt builder
- output parser
- fallback handling for malformed responses

### Minimum Completion Standard

Phase 7 is complete when:

- report generation is predictable
- output formatting is stable across normal cases

### Notes For Execution

- prefer strict JSON output requirements
- keep prompts easy to inspect and iterate on

---

## Phase 8: Add Basic Persistence

### Objective

Store generated reports so analysis results can be revisited.

### Scope

- local database setup
- save report metadata
- save report payload
- optional file metadata storage

### Deliverables

- SQLite database integration
- persistence models or tables
- save and load report behavior
- retrieval endpoint support

### Minimum Completion Standard

Phase 8 is complete when:

- generated reports can be stored and retrieved locally

### Notes For Execution

- keep data storage simple
- avoid overengineering repositories or ORM abstractions if unnecessary

---

## Phase 9: Test The Core Flow

### Objective

Reduce fragility in the main upload-to-report pipeline.

### Scope

- API endpoint tests
- schema validation tests
- analyzer stability tests
- file validation tests

### Deliverables

- automated tests for primary flow
- sample media or mocks for test coverage
- documented known limitations

### Minimum Completion Standard

Phase 9 is complete when:

- the core path is test-covered enough to refactor safely
- common failure cases are caught by tests

### Notes For Execution

- prioritize high-value tests over large quantity
- validate the happy path first

---

## Phase 10: Refine The Product

### Objective

Improve clarity, polish, and user confidence after the first working system exists.

### Scope

- improve wording and report quality
- improve UI readability
- tighten scoring explanations
- improve errors and edge case messaging

### Deliverables

- cleaner report presentation
- better feedback quality
- better docs
- clearer local setup instructions

### Minimum Completion Standard

Phase 10 is complete when:

- the MVP feels coherent and usable rather than merely functional

---

## Execution Rules For Future Requests

If the user later says:

- "Complete Phase 1"
- "Do Phase 5"
- "Start Phase 3 in detail"

Then execution should:

1. Use this document as the default scope definition
2. Implement the phase directly unless the user narrows or expands it
3. Respect work already completed in previous phases
4. Avoid redoing unrelated phases unless necessary
5. Explain any reasonable assumptions made during execution

---

## Suggested Order Of Implementation

Default order:

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6
7. Phase 7
8. Phase 8
9. Phase 9
10. Phase 10

If needed, Phases 2 and 4 can overlap slightly, but schema decisions should be stabilized before frontend expansion.

---

## Important Risks To Remember

- The product may sound more precise than the underlying system really is
- "Audience simulation" should be framed carefully to avoid overclaiming prediction accuracy
- Media processing can become complex quickly, especially video
- LLM output consistency will require deliberate schema control
- Multi-platform support should not be attempted too early

---

## Definition Of A Good MVP

The MVP is successful if:

- a user uploads content
- the system analyzes it without breaking
- the system returns a useful and believable report
- the report helps the creator improve content
- the app is simple, clear, and locally runnable

That is enough for a strong first version.

