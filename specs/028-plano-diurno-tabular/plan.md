# Implementation Plan: Plano diurno e relatório organizado

**Branch**: `028-plano-diurno-tabular` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/028-plano-diurno-tabular/spec.md`

## Summary

Simplify the map to one WAC control and one radar control, restructure the
report as responsive tables with a separate source modal and print appendix,
and calculate a UTC daylight schedule for every route leg on the server. Keep
the route and its existing aircraft/fuel calculations authoritative; store
the schedule in the existing plan-result JSON, and never represent unavailable
solar data or an unverified chart as valid.

## Technical Context

**Language/Version**: Python 3.10+; browser JavaScript remains presentation-only.

**Primary Dependencies**: Existing Flask, SQLAlchemy 2, Alembic, requests,
ReportLab, Leaflet 1.9, Tailwind CSS 4. No new dependency is required.

**Storage**: PostgreSQL 16. Persist schedule data in the existing
`PlanoDeVoo.resultado` JSON field; no schema migration is required. Preserve
the existing `Trecho` relation and its calculated values.

**Testing**: pytest for route selection, AISWEB parsing, schedule boundaries,
HTML, JSON serialization, and PDF output; `npm run css:build` for changed
Tailwind classes; browser checks at 390 px and 1440 px.

**Target Platform**: Authenticated Flask web application, desktop and mobile
browsers.

**Project Type**: Single web application with server-rendered Jinja templates.

**Performance Goals**: Do not add external calls when switching tabs or
rendering the report. Resolve solar data during plan calculation and cache it
per aerodrome/date for that calculation. The generic radar resolver runs only
when the pilot activates the single radar control.

**Constraints**:
- All route, schedule, and source-selection decisions stay on the server.
- All solar and schedule instants are timezone-aware UTC values. Missing or
  malformed AISWEB data produces an unavailable schedule, never a substitute.
- A PDF link is a document, not a georeferenced map. Only a chart matched to
  the route through the official WAC index can be offered as a PDF fallback;
  never select an arbitrary chart or infer coverage from a PDF URL.
- REDEMET remains the radar priority. RainViewer is eligible only for the
  product's educational use, under its current terms, with visible attribution,
  frame time, and coverage caveat.
- Preserve per-pilot authorization, source provenance, educational warnings,
  and existing route/fuel behavior. No secrets are added to source.

**Scale/Scope**: One plan, its existing ordered route legs, the aerodromes in
that route, one active map, and two map controls. The schedule can span
multiple dates; a leg is tried at its requested/available time and, if it does
not fit daylight, at the next sunrise once. If it still cannot fit, that leg's
schedule is unavailable rather than repeatedly deferred or silently given an
extra stop.

## Constitution Check

| Gate | Result | Design response |
|---|---|---|
| I. Specification before code | PASS | `spec.md`, this plan, data model, contracts, and quickstart precede application changes. |
| II. Educational limit | PASS | Preserve the current didactic notice and do not call the route an operational authorization. |
| III. Server-side calculation | PASS | The server calculates ETD/ETA, solar bounds, pernoites, radar source choice, and WAC eligibility. The browser only presents the result and controls layers. |
| IV. Units and provenance | PASS | Keep units and provenance in the source modal and a separate PDF appendix; do not repeat citations beside each report value. Preserve synthetic-profile labels and distinguish unavailable data. |
| V. Small stack and source integrity | PASS | Reuse current Flask/PostgreSQL/AISWEB/REDEMET/Leaflet/ReportLab integrations. No new dependency. Keep WAC official and separate from street maps; use RainViewer only as the attributed educational fallback allowed by the constitution. |
| Access and privacy | PASS | Existing owner-filtered plan routes remain the only entry to plan data and map tiles; new radar metadata uses the same ownership check. No credentials enter page data. |

No constitution gate requires a new principle or an exception.

## Design Decisions

1. **Schedule representation**: Add a `programacao` object under
   `PlanoDeVoo.resultado`, indexed by each leg's existing `ordem`. Store only
   JSON-safe UTC ISO-8601 strings and explicit states. This reuses the plan's
   existing JSON persistence and avoids a migration or a second schedule
   source of truth.
2. **Route versus schedule**: Keep fuel/weight route selection in
   `servidor/rota.py`; do not reject a valid path merely because the requested
   time is too late. A server scheduling step applies solar windows to the
   selected legs. If solar data is missing, preserve the calculated route but
   mark its daylight schedule unavailable; it must not be described as
   daylight-compatible.
3. **Solar source**: Extend `servidor/rotaer_aisweb.py:sol_aerodromo` to return
   both sunrise and sunset for the requested airport/date. Use AISWEB's
   `sol` area and its UTC values. Cache each `(ICAO, UTC date)` within one
   calculation. Do not calculate solar events locally as a fallback.
4. **Per-leg sequencing**: Use the requested departure for the first leg and
   the previous leg's ETA as the next leg's earliest candidate; do not invent
   ground, refuelling, or turnaround time. If a candidate or ETA falls outside
   the relevant solar window, move that leg to the next sunrise at its origin
   once and record the overnight there. If that attempt still fails, return an
   unavailable schedule and do not add an airport not chosen by the route
   engine.
5. **WAC selection**: Keep streets as the implicit base. Show one “Carta WAC”
   control only when the server can prove a current official WAC is usable.
   Render a georeferenced layer only after its edition, calibration,
   reproducibility, and route coverage pass validation. For PDF-only results,
   use AISWEB's current WAC records and official chart-index mapping; open the
   matched PDF, or show the complete route-ordered set when several sheets are
   needed, without portraying them as map layers. If every route-relevant
   sheet cannot be established, omit the control rather than showing a partial
   or wrong chart set.
6. **Radar selection**: Add one authenticated resolver for the existing map
   control. It returns REDEMET first when a valid route product is available,
   otherwise RainViewer only when current terms and coverage metadata permit
   educational use. The browser never chooses a provider. If a REDEMET layer
   fails while loading, it asks the resolver for the next eligible source;
   the same control and status region remain in use. Show the real active
   source, timestamp, linked credit, and coverage caveat for RainViewer.
7. **Source presentation**: Build the report's source rows server-side from
   existing aircraft provenance, leg source fields, ROTAER records, weather,
   wind, chart, and active radar metadata. The main report contains no repeated
   source citations; the accessible “i” dialog and a distinct PDF appendix
   contain the field-to-source table.
8. **Legacy plans**: A saved plan without `resultado.programacao` remains
   readable. Present its schedule as not calculated and do not infer ETD/ETA
   or solar times from a current date; recalculation through the existing plan
   update flow creates a new schedule.

## Project Structure

### Documentation (this feature)

```text
specs/028-plano-diurno-tabular/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── plano-relatorio.md
```

### Source Code

```text
app.py
servidor/
├── planos.py
├── planos_consulta.py
├── rota.py
├── rotaer_aisweb.py
├── tempo.py
├── programacao.py          # new: server-side UTC/daylight sequencing
└── pdf_plano.py
templates/
└── plano.html
static/css/
├── input.css
└── tailwind.css            # generated by the existing CSS build
tests/
├── test_rota.py
├── test_tempo.py
├── test_catalogo_aerodromos.py
├── test_programacao.py   # new: solar schedule boundaries and pernoites
├── test_tela_piloto.py
├── test_rota_pdf.py
└── focused schedule/map/source tests
```

**Structure Decision**: Extend the existing single Flask application. Keep
external data acquisition in its current provider modules, isolate the new
date/solar sequencing in `servidor/programacao.py`, orchestrate it in
`servidor/planos.py`, and expose its result through the existing plan view and
JSON serializer. The report and PDF remain the existing template and
ReportLab pipeline.

## Complexity Tracking

No constitution violations or new dependencies require justification.
