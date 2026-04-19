# Future Plans

This document continues the Audience roadmap from Phase 10 onward.

It is based on the current repository state, the current SQLite database, and the product direction of running `Llama 3.2 3B` locally for audience simulation.

## Current Baseline Analysis

The current project is a strong MVP, but it is still a single-report system rather than a full audience simulator.

- The live database is `backend/data/audience.db`.
- The database currently has one table only: `reports`.
- That table stores one saved report per run plus embedded `report_json` and `analysis_json`.
- The current database contains 23 reports: 16 `image` runs and 7 `short_video` runs.
- All saved runs target only `instagram_reels`.
- The current backend report schema is still single-audience and centered on `hook_score`, `engagement_score`, `boring_rate`, `peak_moments`, `simulated_comments`, `final_verdict`, and `improvements`.
- Transcript support is still a placeholder, and `audio_present` is reserved but not yet implemented.
- The frontend is functional, but it does not yet follow the warm parchment-based design system in `DesignGuidelines.md`.

## Main Gap Between The MVP And The Full Vision

To reach the real product vision, the system must grow from:

- one uploaded file
- one normalized media analysis
- one generated report

into:

- one simulation run with many agents
- many agent personas with configurable traits
- consent-aware handling for sensitive audience lenses
- per-agent and combined emotion scoring
- timeline-based emotional spikes and narrative summaries
- support for short-form video, image, audio, music, and platform-specific contexts
- a much richer database model than the current single `reports` table

## Rules For All Remaining Phases

- Keep the product honest. It is a prediction aid, not a truth engine.
- Keep the system local-first and realistic for a laptop running `Llama 3.2 3B`.
- Preserve the current MVP flow while adding the new simulation architecture beside it.
- Treat sensitive traits carefully. Religion or similar protected lenses must be opt-in, consent-gated, and explanation-focused.
- Avoid race-based or stereotype-based simulation packs. If regional context is needed, model it as culture or market context, not as biased identity assumptions.
- All new UI work must follow `DesignGuidelines.md`.
- All report outputs should show uncertainty, disagreement, and evidence instead of pretending to be certain.

## Phase 11: Freeze The Simulation 2.0 Contract

Goal: define the exact shape of the post-MVP product before large implementation work starts.

Main deliverables:

- a `SimulationRun v2` contract that separates media analysis, agent setup, agent outputs, and final report output
- official run modes such as `quick`, `standard`, `deep`, and `custom`
- clear local runtime limits for laptop execution, including media duration caps and agent-count caps
- a formal distinction between `generic agent presets` and `custom agent builder`
- a safety policy for optional sensitive audience lenses

Done when:

- the backend, frontend, and database teams can all build against one stable v2 contract
- there is no ambiguity about what counts as a single simulation run

## Phase 12: Rebuild The Database For Multi-Agent Simulation

Goal: replace the MVP's single-table persistence model with a schema that can support full simulation history.

Why this phase is required:

- the current `reports` table cannot cleanly represent multiple agents, timeline traces, consent records, or repeated runs on the same asset

Main database work:

- keep the current `reports` table for backward compatibility during migration
- add normalized tables for `media_assets`, `simulation_runs`, `run_targets`, `agent_profiles`, `agent_runs`, `emotion_samples`, `timeline_events`, `consent_records`, and `report_exports`
- store both normalized fields and selected JSON snapshots for easy replay
- add migration scripts so old MVP reports can still appear in history
- add indexes for recent runs, asset reuse, and agent-run lookup

Done when:

- one simulation run can store many agents and many timeline points
- old MVP reports still load without data loss

## Phase 13: Expand The Media Intake Layer

Goal: support the kinds of media creators actually want to test before posting.

Main scope:

- keep `image` and `short_video`
- add `audio`, `music`, and mixed audio-video support
- prepare the pipeline for `youtube_shorts` alongside `instagram_reels`
- enforce strict duration and file-size limits by mode so local execution stays practical

Main backend work:

- extend media detection and validation contracts
- add audio waveform analysis, energy curves, silence detection, and beat or intensity markers
- replace the transcript placeholder with real speech-to-text
- improve OCR and on-screen text extraction for short-form content
- segment every input into reusable evidence units such as frames, scenes, speech chunks, and audio moments

Done when:

- the analysis pipeline can produce a stable multimodal evidence package for image, short video, audio, and music

## Phase 14: Build The Local Llama Runtime Layer

Goal: make multi-agent simulation practical on a normal laptop using `Llama 3.2 3B`.

Main scope:

- add a simulation runner that can schedule many agent prompts safely
- create quality modes so users can trade speed for depth
- keep memory pressure and latency predictable

Main engineering work:

- add prompt budgeting and context compression
- cache reusable media evidence so each agent does not reprocess the same raw content
- add local benchmarking for tokens, latency, memory, and per-agent cost
- support controlled parallelism where the machine can handle it, with queue-based fallback when it cannot
- add resume and retry behavior for long local runs

Done when:

- the app can run a realistic multi-agent simulation locally without freezing the laptop

## Phase 15: Agent Presets, Custom Agents, And Consent Flow

Goal: let the user choose between a fast preset simulation and a carefully customized audience panel.

Main product scope:

- generic mode where the system auto-builds a balanced audience panel
- custom mode where the user chooses the number of agents and their traits
- clear UX for age bands, gender lenses, experience level, and platform behavior style

Sensitive-lens rules:

- religion-aware or similar protected-context lenses must be disabled by default
- the user must explicitly opt in and confirm they understand the feature is only a hypothetical context lens
- these lenses should be framed as viewpoint context, not as claims about real people
- region should be modeled as audience market or cultural context, not as race-based profiling

Main deliverables:

- `agent_profile` schema
- preset libraries
- custom-agent builder rules
- consent capture and audit storage

Done when:

- a user can run either a preset audience panel or a custom panel such as six specific agents

## Phase 16: Multi-Agent Simulation Engine

Goal: turn one report into a real audience panel.

Main scope:

- run each agent against the same evidence package
- let each agent produce its own reaction, emotional interpretation, retention opinion, and comment
- aggregate the panel into consensus and disagreement signals

Main backend work:

- build agent-specific prompt templates
- add run orchestration for many agents per simulation
- store raw agent outputs, parsed outputs, and normalized scores
- add ensemble logic for combined scoring and conflict detection
- expose run progress so the frontend can show partial completion

Done when:

- one simulation can return per-agent reactions plus a combined panel summary

## Phase 17: Emotion Scoreboard And Timeline Intelligence

Goal: deliver the exact scoreboard behavior requested for the product.

Main scope:

- per-agent emotion scoring
- combined all-agent emotion scoring
- timestamped spikes for happiness, sadness, laughter, surprise, confusion, tension, and drop-off risk
- a narrative paragraph explaining how the emotional journey unfolded

Example outcome of this phase:

- if a joke lands at `0:03`, the report should call out a happiness or laughter spike at `0:03`
- if pacing slows at `0:11`, the report should show a dip in attention or rising boredom there

Main deliverables:

- new emotion schema for scoreboard metrics
- time-series storage in the database
- spike detection logic
- narrative generator for the emotion arc
- combined score calculation rules across all agents

Done when:

- the report can show both summary emotion scores and a believable emotional timeline

## Phase 18: Report Schema V2 And Explainability

Goal: redesign the output contract so it matches the full simulation product rather than the MVP report.

Main report sections:

- executive summary
- platform readiness score
- combined scoreboard
- per-agent reaction cards
- timeline spikes and emotional arc
- agreement versus disagreement across agents
- strengths, risks, and improvement suggestions
- confidence and limitation notes

Main backend work:

- define `Audience Simulation Report v2`
- version report contracts so old reports still render
- attach evidence traces so users can see why the system made a claim
- add export-friendly shapes for Markdown, PDF, and future share views

Done when:

- the full report can explain not only what the panel thinks, but why it thinks it

## Phase 19: Platform Expansion Beyond The MVP

Goal: make the simulation truly useful for real creator workflows.

Main scope:

- keep `instagram_reels`
- add `youtube_shorts`
- add a `generic short-form` option for unsupported platforms
- make audio and music analysis first-class citizens for content planning

Main product intelligence:

- platform-specific hook windows
- platform-specific pacing expectations
- platform-specific caption and text-overlay guidance
- separate verdict framing for visual-only, audio-only, and mixed media cases

Done when:

- the same content can be simulated differently depending on platform context

## Phase 20: Frontend Redesign To Match Design Guidelines

Goal: bring the product UI up to the design standard defined in `DesignGuidelines.md`.

Why this phase matters:

- the current frontend works, but its dark purple MVP styling does not match the intended product identity

Main design and frontend work:

- move the app to the parchment, ivory, terracotta, and warm-neutral palette
- use serif-led editorial hierarchy for major headings and warm sans UI text
- build a simulation setup flow for generic and custom modes
- add consent modals for sensitive lenses
- create a scoreboard view, per-agent cards, and a timeline visualization
- make recent runs, report comparison, and export views feel like one coherent product
- keep the layout responsive for laptop and mobile review

Done when:

- the product looks and feels consistent with the design system, not like an MVP placeholder

## Phase 21: Performance, Caching, And Creator Workflow Speed

Goal: make the simulator practical for repeated everyday use.

Main scope:

- caching for media evidence extraction
- rerun logic when only agent settings change
- compare mode for multiple content versions
- quick preview versus full deep simulation
- batch queue for multiple uploads

Main engineering work:

- asset fingerprinting
- reusable evidence caches
- partial rerun support
- local job queue and cancellation support
- better loading and progress reporting

Done when:

- creators can iterate quickly instead of waiting for every run to start from zero

## Phase 22: Evaluation, Safety, And Trust Calibration

Goal: prove the product is useful without overclaiming what it knows.

Main scope:

- human evaluation datasets for reaction quality
- fairness and safety review for persona prompts and sensitive-lens behavior
- red-team testing for offensive, biased, or overconfident outputs
- score calibration so the system does not sound more accurate than it is

Main deliverables:

- benchmark suite
- safety test cases
- documented limitations
- confidence framing rules
- release checklist for sensitive features

Done when:

- the product can defend its claims, explain its limits, and avoid harmful behavior

## Phase 23: Report Comparison, Versioning, And Pre-Upload Decision Tools

Goal: help creators use the simulator as a real decision-making platform before posting.

Main scope:

- compare two or more cuts of the same content
- compare caption variants, thumbnails, or openings
- keep version history tied to one asset family
- show whether edits improved the combined audience response

Main deliverables:

- version comparison UI
- delta report logic
- improvement-over-time charts
- save-as-draft and rerun workflows

Done when:

- creators can use Audience to decide which version is strongest before publishing

## Phase 24: Full Project Completion And Release Hardening

Goal: finish the product as a coherent local-first creator platform.

Main scope:

- polish installation and onboarding
- stabilize migrations, export behavior, and long-term storage rules
- package the app for reliable local setup
- finalize docs for normal non-technical users
- complete release hardening across backend, frontend, database, and simulation quality

Definition of full-project completion:

- a user can upload short-form media or audio content
- the app can run multiple local `Llama 3.2 3B` audience agents
- the user can choose preset or custom audiences
- optional sensitive audience lenses are consent-gated and safe by default
- the report includes per-agent reactions, combined scores, and timeline spikes
- Instagram Reels and YouTube Shorts are both supported
- the UI follows `DesignGuidelines.md`
- the product clearly communicates that results are predictive guidance, not certainty

## Recommended Execution Order

The safest build order is:

1. Phase 11
2. Phase 12
3. Phase 13
4. Phase 14
5. Phase 15
6. Phase 16
7. Phase 17
8. Phase 18
9. Phase 19
10. Phase 20
11. Phase 21
12. Phase 22
13. Phase 23
14. Phase 24

## Highest-Priority Immediate Focus

If implementation starts right away, the first serious build block should be:

1. Phase 11: lock the v2 contract
2. Phase 12: redesign the database
3. Phase 14 and Phase 15 together: prove the local multi-agent runtime and persona system

Without those three foundations, later scoreboard and platform features will become fragile.
