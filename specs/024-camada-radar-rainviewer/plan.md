# Implementation Plan: Camada suplementar de radar RainViewer

**Branch**: `024-camada-radar-rainviewer` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/024-camada-radar-rainviewer/spec.md`

## Summary

Add a user-activated RainViewer radar overlay as a non-official layer, keeping the existing REDEMET radar independent and unchanged. Reuse Leaflet and the existing authenticated plan-map flow; fetch the public RainViewer manifest and proxy validated radar and coverage tiles through fixed server endpoints. Display provider attribution, frame time, coverage mask, and explicit unavailable states. Do not persist the source response, alter route calculations, or add dependencies.

## Technical Context

**Language/Version**: Python 3.10+, Flask, Jinja, and existing browser JavaScript.

**Primary Dependencies**: Existing `requests`, Flask, SQLAlchemy, and Leaflet; no new dependency.

**Storage**: PostgreSQL remains unchanged; frame and coverage metadata are request-scoped and are not saved to plans.

**Testing**: Focused pytest tests for the provider client and authenticated map routes, plus existing plan-screen tests. External responses are mocked for deterministic tests.

**Target Platform**: Existing Linux Flask server and responsive browser UI.

**Project Type**: Server-rendered web application.

**Performance Goals**: Do not contact RainViewer when opening a plan or switching map bases. Fetch the manifest only after explicit activation; request only visible map tiles and pass through provider cache headers where available.

**Constraints**: RainViewer's current public terms permit educational use with visible attribution but provide no SLA or guaranteed coverage. Use only a fixed provider host and validated frame/tile coordinates. Keep the official REDEMET layer independent; do not silently fall back between providers. Use the provider's coverage mask so uncovered areas are not confused with no precipitation. No new secret, dependency, persistent model, or migration.

**Scale/Scope**: `servidor/rainviewer.py`, authenticated routes in `app.py`, the map controls in `templates/plano.html`, focused tests, and `documentacao/piloto.md`.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| I. Specification before code | PASS | Feature 024 has a spec, plan, and tasks before application edits. |
| II. Educational boundary | PASS | RainViewer is explicitly non-official, supplementary, and excluded from operational calculations or authorization. |
| III. Calculation and weather on server | PASS | The server obtains the manifest and proxies provider tiles; the browser only requests application routes and renders results. |
| IV. Units and source explicit | PASS | The overlay shows RainViewer attribution and frame time when supplied; missing coverage remains visibly distinct from precipitation. |
| V. Small stack and relational database | PASS | Existing requests/Flask/Leaflet are reused; REDEMET remains official and separate; no schema or dependency change. |
| Pilot access and source restrictions | PASS | Plan-owned routes remain authenticated. RainViewer use is limited to current permitted educational terms, with visible attribution and no silent fallback. |

No constitutional violation identified.

## Project Structure

### Documentation (this feature)

```text
specs/024-camada-radar-rainviewer/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── camadas-rainviewer.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
servidor/rainviewer.py           # Fetch and validate manifest, radar, and coverage tiles
app.py                           # Authenticated plan-owned manifest/tile proxy routes
templates/plano.html             # Optional overlay controls, attribution, status, and coverage cue
tests/test_rainviewer.py         # Provider contract, validation, and error cases
tests/test_tela_piloto.py        # Route ownership and map-layer integration behavior
documentacao/piloto.md           # Explain non-official source and coverage limitations
```

**Structure Decision**: Add a small provider module alongside `servidor/openaip.py` rather than expanding `servidor/tempo.py`. Reuse existing authenticated owner checks and Leaflet controls. All external requests use fixed provider hosts and bounded identifiers; the client never receives or controls an arbitrary upstream URL.

## Phase 0: Outline & Research

- `research.md` records current RainViewer API behavior, public-use terms, Brazil source list, coverage-mask limitations, and the INPE/CPTEC alternative.
- Use only the newest frame listed in the RainViewer radar manifest; display its frame timestamp, not the manifest-generation timestamp.
- Use RainViewer's documented coverage tiles to distinguish uncovered areas from areas with no radar echo. If coverage tiles cannot load, report the overlay as unavailable or coverage unknown rather than implying dry weather.
- The database API for radar stations is deprecated; do not rely on it for coverage metadata.
- INPE/CPTEC products are a credible Brazilian public-data alternative, but no stable public XYZ-tile contract was found for this feature. Keep that option out of this implementation.

## Phase 1: Design & Contracts

- `data-model.md` defines request-scoped manifest/frame, overlay state, and coverage tile data; no persistence is added.
- `contracts/camadas-rainviewer.md` defines authenticated application routes for manifest and validated radar/coverage tiles.
- `quickstart.md` describes mocked tests and a manual live-source check for the current route, visible attribution, frame time, and coverage mask.
- Post-design Constitution Check: PASS. The RainViewer layer is optional and non-official; it cannot replace or mutate REDEMET, WAC, the route, or calculations.

## Complexity Tracking

No violations or additional abstractions to justify.
