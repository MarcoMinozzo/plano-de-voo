# Implementation Plan: Filtro integrado na seleção de aeródromos

**Branch**: `012-filtro-integrado-aerodromos` | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/012-filtro-integrado-aerodromos/spec.md`

## Summary

Replace the separate origin/destination filter controls with one accessible searchable selector per field, progressively enhancing the existing native selectors. Preserve a functional native fallback and submit the selected ICAO through the existing field; leave backend validation and route calculation unchanged.

## Technical Context

**Language/Version**: Python 3.10+ server; Jinja, HTML and vanilla JavaScript in the existing page.

**Primary Dependencies**: Existing Flask/Jinja stack; no new dependencies.

**Storage**: No schema or storage changes; existing aerodrome catalog only.

**Testing**: pytest for rendered form and submission behavior; Node.js for the existing pattern of focused JavaScript search checks.

**Target Platform**: Existing responsive Flask web application.

**Project Type**: Monolithic web application.

**Performance Goals**: Search the already-rendered catalog locally without network requests; keep the result list scrollable and usable on narrow screens.

**Constraints**: Preserve labels, current selected values on validation responses, ICAO form field names, and support for both national and local catalogs. No route, catalog, database, or calculation changes.

**Scale/Scope**: One template and its focused UI tests, plus feature documentation.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| I. Specification before code | PASS | Feature spec, plan, and tasks precede UI edits. |
| II. Educational boundary | PASS | No change to flight results or educational notices. |
| III. Server-side calculations | PASS | UI only selects existing catalog values; routing remains on the server. |
| IV. Explicit sources and units | PASS | Existing catalog entries and provenance are not altered. |
| V. Small stack and relational database | PASS | No dependency, schema, or database change. |
| Pilot access | PASS | Existing authenticated form and ownership behavior are untouched. |

No constitutional violation identified.

## Project Structure

### Documentation

```text
specs/012-filtro-integrado-aerodromos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── selecao-aerodromo.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
templates/plano_novo.html   # Origin/destination selectors and accessible interaction
tests/test_tela_piloto.py   # Search, selection, submission, and retained values
```

**Structure Decision**: Keep the interaction in the existing server-rendered form. The browser filters the catalog already supplied by the page; the form continues posting the existing `origem` and `destino` ICAO identifiers.

## Phase 0: Outline & Research

- `research.md` records that the approved experience already calls for a select whose text filters by code or displayed name. The current implementation instead renders separate search inputs and native selects.
- Reuse accent-insensitive substring matching and the existing catalog data. No unknown technology, external service, or new dependency requires additional research.
- The selector contract defines searching, choosing, invalid free text, keyboard behavior, restoration after server validation, and the no-JavaScript fallback.

## Phase 1: Design & Contracts

- `data-model.md` confirms that selection is transient and introduces no stored entity.
- `contracts/selecao-aerodromo.md` specifies the user-facing selector interaction; no external API contract changes.
- `quickstart.md` documents the focused regression command.
- Constitution check remains PASS: no calculation, catalog source, persistence, or dependency changes.

## Complexity Tracking

No violations or additional abstractions to justify.
