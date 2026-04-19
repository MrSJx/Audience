# Phase 11 Simulation Contract

Phase 11 freezes the `Simulation 2.0` contract before the multi-agent runtime is built.

## What was added

- typed Phase 11 models in [backend/app/models/simulation.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/models/simulation.py>)
- a schema snapshot endpoint at `GET /simulation-schema`
- explicit runtime modes: `quick`, `standard`, `deep`, and `custom`
- a stable separation between:
  - target media context
  - audience panel definition
  - consent requirements
  - per-agent outputs
  - combined panel output
  - final report output

## Why this phase matters

The MVP contract only supports one analysis and one report.

The future product needs a frozen contract for:

- multiple agents
- preset and custom panels
- per-agent reactions
- combined scoreboard output
- timeline spikes
- sensitive-lens consent handling

Without this contract freeze, later implementation would keep changing schema assumptions mid-build.

## Sensitive-lens rule now locked

- sensitive audience lenses are not part of default generic presets
- any religion-aware lens must be explicit, opt-in, and consent-gated
- regional context should be modeled as market or cultural context, not as race-based profiling

## Current implementation boundary

Phase 11 freezes the contract and exposes it for inspection.

It does not yet run the full multi-agent simulation engine. That work starts in later phases.
