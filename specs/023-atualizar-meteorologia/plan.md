# Implementation Plan: Atualizar meteorologia ao consultar o plano

**Branch**: `023-atualizar-meteorologia` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/023-atualizar-meteorologia/spec.md`

## Summary

Refresh METAR/TAF for each distinct aerodrome in a saved plan and refresh route radar when the detail page is requested. Reuse the existing AWC and REDEMET clients, present fresh results in HTML and JSON without writing during GET, and preserve explicit unavailable states. Do not call unrelated wind or chart services, recalculate the route, or trigger requests from map controls.

## Technical Context

**Language/Version**: Python 3.10+, Flask, Jinja, and existing browser JavaScript.

**Primary Dependencies**: Existing `requests`, Flask, and SQLAlchemy; no new dependency.

**Storage**: PostgreSQL. Existing plan weather JSON remains unchanged by detail-page GET; current results are request-scoped presentation data.

**Testing**: Focused pytest coverage in `tests/test_tempo.py` and `tests/test_tela_piloto.py`; provider responses are mocked for deterministic coverage.

**Target Platform**: Existing Linux Flask server and responsive browser UI.

**Project Type**: Server-rendered web application.

**Performance Goals**: One METAR and one TAF lookup per distinct route aerodrome, plus one radar lookup per detail request when configured. No new requests when switching fiches or map layers. Existing HTTP timeout remains in force; external-source latency is not controlled by the application.

**Constraints**: AWC and REDEMET remain the sources. Missing observations, credentials, coverage, or provider responses remain unavailable without fallback or invented values. Preserve authorization, route, calculations, plan inputs, and stored snapshots. Keep credentials outside version control.

**Scale/Scope**: `app.py`, `servidor/tempo.py`, `templates/plano.html`, and focused tests. No schema migration, new endpoint, dependency, or PDF change.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| I. Specification before code | PASS | Feature 023 has `spec.md`; this plan and tasks precede implementation. |
| II. Educational boundary | PASS | The change presents source data and unavailability only; it adds no operational recommendation or flight authorization. |
| III. Calculation and weather on server | PASS | The server obtains weather; the browser only renders returned data and controls map presentation. |
| IV. Explicit units and sources | PASS | Existing source, observation time, raw report, units, and unavailable states are preserved; no values are inferred. |
| V. Small stack and relational database | PASS | Existing clients and database fields are reused; no new dependency, schema, or secret is introduced. |
| Pilot access and source restrictions | PASS | Existing plan-owner check is preserved; radar remains REDEMET-only and unavailable without valid data. |

No constitutional violation identified.

## Project Structure

### Documentation (this feature)

```text
specs/023-atualizar-meteorologia/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── consulta-plano.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
app.py                       # Prepare live weather for the authenticated plan response
servidor/tempo.py            # Reuse AWC METAR/TAF and REDEMET radar lookups
servidor/planos.py           # Existing plan creation/edit snapshot; no route changes
templates/plano.html         # Render request-scoped weather and radar state
tests/test_tempo.py          # Source results, unavailable states, and deduplication
tests/test_tela_piloto.py    # HTML/JSON freshness, authorization, and map behavior
```

**Structure Decision**: Keep the existing Flask application and source clients. Build a request-scoped weather/radar result from the saved plan's route in the detail handler; pass it to both the HTML view and JSON serializer. Do not persist it during GET, and do not call the broader `buscar` operation because that also requests wind and charts. Keep map controls client-side and independent of source retrieval.

## Phase 0: Outline & Research

- `research.md` records that plan creation/edit calls `tempo.buscar` and stores a snapshot, while the existing detail GET reads that snapshot without refreshing.
- Reuse `meteorologia` and `radar`; query every distinct route aerodrome once for each METAR/TAF product and query radar once for the saved plan's origin/destination.
- A live source check returned HTTP 204 for SBJD and a current METAR for SBGR. HTTP 204 is a valid no-observation result, not a reason to use a nearby station.
- `carregar_env()` does not find `REDEMET_API_KEY` in the local configuration. Radar network behavior therefore cannot be verified against the live provider here; test success and missing-key behavior with simulated responses, and keep real radar unavailable until a valid key is configured.
- The new detail lookup must not call `buscar`, since that would also re-fetch wind and chart data unrelated to this request.

## Phase 1: Design & Contracts

- `data-model.md` documents the existing saved plan and request-scoped meteorology/radar values; no persistent schema change is needed.
- `contracts/consulta-plano.md` records that HTML and JSON keep their existing access and shape while weather fields reflect the current detail request.
- `quickstart.md` describes focused mocked-source tests and browser checks, including explicit radar unavailability without a key.
- Post-design Constitution Check: PASS. No client-side calculation, secret, new dependency, migration, route mutation, or silent fallback is introduced.

## Complexity Tracking

No violations or additional abstractions to justify.
