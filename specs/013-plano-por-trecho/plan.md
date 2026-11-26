# Implementation Plan: Tela do plano organizada por trecho

**Branch**: `013-plano-por-trecho` | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/013-plano-por-trecho/spec.md`

## Summary

Reorganize the calculated-plan page into accessible, selectable leg fichas, each showing only its own route points, weather, measurements, and sequence. Keep one Leaflet map instance and update its displayed leg when the active ficha changes. Present the official WAC as explicitly unavailable until the existing source-validation gates pass; keep streets, eligible OpenAIP, and an independently controlled radar. Extend the persisted METAR snapshot with structured AWC fields, render supported fields in Portuguese alongside unchanged raw METAR, and keep TAF raw. Remove interactive checklist controls from the page while preserving the PDF.

## Technical Context

**Language/Version**: Python 3.10+; Jinja templates, HTML, and vanilla JavaScript.

**Primary Dependencies**: Existing Flask, SQLAlchemy, requests, Leaflet 1.9, and Tailwind CSS; no new dependency.

**Storage**: Existing PostgreSQL `PlanoDeVoo.meteorologia` JSON field; no schema migration.

**Testing**: Focused pytest tests for AWC data shaping, plan-page rendering and state transitions, and PDF non-regression. Browser validation at 390 px and 1440 px.

**Target Platform**: Existing responsive Flask web application.

**Project Type**: Server-rendered web application.

**Performance Goals**: No additional external requests when switching fichas or map layers; one map instance updates locally from the calculated plan.

**Constraints**: Do not change route calculations, persisted route legs, plan ownership, or PDF output. Render only fields returned by AWC, preserve raw METAR, and mark missing/unsupported details explicitly. WAC remains unavailable until all gates in feature 009 are evidenced. OpenAIP follows feature 010 and the constitution. No new dependencies.

**Scale/Scope**: `app.py`, `servidor/planos.py`, `servidor/tempo.py`, `templates/plano.html`, focused tests, and pilot-facing documentation if needed.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| I. Specification before code | PASS | Feature 013 spec precedes template and server changes. |
| II. Educational boundary | PASS | Existing educational, estimate, DEMO, and no-flight-authorization notices stay visible; no operational recommendation is added. |
| III. Calculation and weather on server | PASS | AWC data is captured and prepared server-side; JavaScript only changes the displayed ficha and map layers. |
| IV. Explicit units and sources | PASS | Render only available AWC fields with units, source, and observation time; retain raw report and explicit missing state. |
| V. Small stack and relational database | PASS | Reuse the JSON field and installed dependencies; no migration or secret is introduced. WAC/OpenAIP restrictions remain. |
| Pilot access | PASS | Existing plan ownership checks remain unchanged. |

No constitutional violation identified.

## Project Structure

### Documentation

```text
specs/013-plano-por-trecho/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── tela-plano.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
app.py                       # Prepare coordinates per stored leg for the page
servidor/planos.py           # Retrieve weather for each distinct aerodrome on the route
servidor/tempo.py            # Capture and present optional structured AWC METAR fields
templates/plano.html         # Active leg ficha, map controls, weather and sequence
tests/test_tempo.py          # Verify AWC fields and missing-value handling
tests/test_rota.py           # Verify per-route weather retrieval
tests/test_tela_piloto.py    # Verify leg tabs, map scope, weather and unavailable layers
tests/test_casca_visual.py   # Verify summary/ficha hierarchy and no screen checklist
documentacao/piloto.md       # Explain the screen controls and translated weather
```

**Structure Decision**: Keep server-rendered plan data and the existing Leaflet integration. The route and each leg are already persisted; the view prepares the corresponding endpoints for presentation. Use progressive enhancement for the ficha selector so all leg content remains reachable without JavaScript. One map instance receives only the active leg's two endpoints; changing tabs does not call the route or weather services.

## Phase 0: Outline & Research

- `research.md` records the AviationWeather.gov API contract for its JSON METAR observation fields and confirms that the raw report and structured fields can be retained together.
- Use only source-returned METAR fields for Portuguese labels and explanations. Do not infer cloud, visibility, wind, or phenomena values from missing fields; preserve unhandled codes in the untouched raw report and identify unsupported fields.
- The existing WAC GeoPDF gates remain binding. The WAC control communicates unavailability unless those gates have documented evidence; never substitute streets or OpenAIP as a WAC.
- Reuse existing Leaflet, OpenAIP endpoint, radar overlay, map attribution, and active-plan authorization.
- No dependency or database schema change is needed.

## Phase 1: Design & Contracts

- `data-model.md` defines additional optional source-returned METAR fields and weather keyed by aerodrome in the existing plan weather JSON; no new persisted entity is introduced.
- `contracts/tela-plano.md` defines tab/panel behavior, map scope, layer availability, weather presentation, and no-JavaScript fallback.
- `quickstart.md` describes focused tests and manual responsive/accessibility scenarios.
- Post-design Constitution Check remains PASS: no browser-side calculation, invented data, hidden source failure, new dependency, or change to PDF/ownership.

## Complexity Tracking

No violations or additional abstractions to justify.
