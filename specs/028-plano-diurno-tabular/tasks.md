---
description: "Tarefas para implementar o plano diurno e relatório organizado"
---

# Tasks: Plano diurno e relatório organizado

**Input**: Design documents from `specs/028-plano-diurno-tabular/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/plano-relatorio.md`, `quickstart.md`

**Tests**: Incluídos testes focados para os cenários e critérios de aceitação
definidos na spec e no quickstart.

**Organization**: Tasks are grouped by user story so each increment can be
implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with another task when files and prerequisites
  do not overlap.
- **[Story]**: User story from `spec.md` (`US1`, `US2`, or `US3`).
- Cada tarefa indica os caminhos exatos dos arquivos envolvidos.

## Phase 1: Setup

**Purpose**: Project initialization and shared infrastructure.

No setup task is required: the existing Python environment, Flask application,
PostgreSQL database, pytest suite, and Tailwind build are already configured.
This feature introduces no dependency.

---

## Phase 2: Foundational

**Purpose**: Blocking prerequisites for all user stories.

No separate foundational task is required. Existing session authentication,
per-plan ownership checks, provider integrations, and `PlanoDeVoo.resultado`
JSON persistence provide the shared foundation.

---

## Phase 3: User Story 1 - Consultar mapa com controles simples (Priority: P1) 🎯 MVP

**Goal**: Present a single route-aware WAC control and a single radar control,
with provider selection performed on the server and a responsive map.

**Independent Test**: Open plans with a validated WAC layer, route-matched
official PDF sheets, and no usable WAC; exercise REDEMET, RainViewer, and
unavailable radar states. Confirm one WAC control at most, one radar control,
no Google Maps/OpenAIP/separate-street controls, no wrong or partial WAC
coverage, and usable controls at 390 px and 1440 px.

### Tests for User Story 1

- [X] T001 [P] [US1] Update WAC selection cases in `tests/test_tempo.py` to cover current VFR/WAC records, complete route-to-index matching, multiple route-ordered PDFs, and hidden/unavailable results when official coverage cannot be proven.
- [X] T002 [P] [US1] Add map and radar resolver cases in `tests/test_tela_piloto.py` for one visible radar control, WAC control visibility, provider priority/fallback, single retry, invalid `exclude` values, and plan-owner authorization.

### Implementation for User Story 1

- [X] T003 [P] [US1] Implement current AISWEB WAC selection in `servidor/tempo.py`; use official chart-index matching for every route leg, return the complete ordered PDF set when needed, and never infer bounds or choose an arbitrary/partial chart.
- [X] T004 [P] [US1] Add `GET /planos/<plano_id>/camadas/radar` in `app.py`; enforce session and plan ownership, select REDEMET before eligible RainViewer, accept only the documented single retry exclusion, and return source, frame time, attribution, coverage caveat, or an explicit unavailable state.
- [X] T005 [US1] Replace redundant map controls in `templates/plano.html` with at most one “Carta WAC” and one “Radar de chuva” control; remove Google Maps, OpenAIP, separate street-map and provider-specific radar controls/messages, and make the controls and PDF list accessible and usable on small screens.

**Checkpoint**: WAC and radar behavior can be validated independently of the
report redesign and solar scheduling.

---

## Phase 4: User Story 2 - Ler o relatório e consultar fontes (Priority: P1)

**Goal**: Organize report information into responsive tables, show route and
verified airport contacts, and move provenance into an accessible dialog and
separate PDF appendix.

**Independent Test**: Open a plan with multiple legs and available/missing
airport contacts. Confirm the full ordered route and airport names, tables,
text-labelled red limit alerts, the source dialog, and a separate PDF source
appendix without citations repeated beside values.

### Tests for User Story 2

- [X] T006 [P] [US2] Add report assertions in `tests/test_tela_piloto.py` for the first full-route card, full airport names, verified-only contacts, responsive tables, red alerts with explanatory text, source dialog, top print action, and removal of inline citations, “Como ler este plano”, and bottom print action.
- [X] T007 [P] [US2] Add PDF provenance assertions in `tests/test_rota_pdf.py` for a field-to-source appendix separate from the main report body and airport contact provenance where available.

### Implementation for User Story 2

- [X] T008 [US2] Build report source rows and route endpoint contact data in `servidor/planos_consulta.py` and `app.py`; include the `FonteRelatorio` fields `campo`, `fonte`, `publicador`, `referencia`, `data`, `unidade`, `aplicabilidade`, and `estado`, expose contacts only when `contatos_rotaer_verificados` is true, and leave missing metadata unavailable rather than inferring it.
- [X] T009 [P] [US2] Reorganize `templates/plano.html` into a complete route-first card and responsive information tables; add the accessible field/source dialog beside print, show verified endpoint contacts, keep red limit alerts understandable without color, and remove redundant source text/help/bottom print.
- [X] T010 [P] [US2] Update `servidor/pdf_plano.py` and `servidor/pdf_layout.py` to present related report fields in tables and render provenance in a separate appendix rather than beside each value.

**Checkpoint**: The HTML and PDF report are independently readable and retain
source traceability.

---

## Phase 5: User Story 3 - Planejar trechos dentro do período diurno (Priority: P1)

**Goal**: Persist and present server-calculated UTC ETD/ETA, sunrise/sunset,
next-day delays, and overnight locations for each route leg.

**Independent Test**: Calculate single- and multi-leg routes with valid,
missing, and malformed AISWEB solar data. Confirm that accepted schedule
instants satisfy `ETD >= origin sunrise`, `ETD <= origin sunset`,
`ETA <= destination sunset`, and `ETA >= ETD`; a delayed leg identifies its
origin/date overnight; an unfit leg or unavailable solar input is not declared
daylight-compatible; legacy plans remain readable without invented times.

### Tests for User Story 3

- [X] T011 [P] [US3] Extend AISWEB solar tests in `tests/test_catalogo_aerodromos.py` to verify sunrise and sunset parsing from `area=sol`, UTC awareness, requested ICAO/date parameters, and unavailable results for missing or malformed values.
- [X] T012 [P] [US3] Create `tests/test_programacao.py` and extend `tests/test_rota.py` with deterministic cases for before-sunrise departure, sunset equality/overflow, one next-sunrise retry, per-leg overnight sequencing, missing solar data, a leg that still does not fit, and unchanged fuel-based route choice.
- [X] T013 [P] [US3] Add saved-plan rendering and PDF cases in `tests/test_tela_piloto.py` and `tests/test_rota_pdf.py` for ETD/ETA, solar bounds, multiple dates, pernoites, unavailable schedules, and legacy plans without `resultado.programacao`.

### Implementation for User Story 3

- [X] T014 [US3] Extend `sol_aerodromo` in `servidor/rotaer_aisweb.py` to parse both sunrise and sunset for the requested aerodrome/date, require timezone-aware UTC instants, and report incomplete or invalid responses as unavailable without a local calculation fallback.
- [X] T015 [US3] Implement the bounded per-leg scheduler in `servidor/programacao.py` and remove sunset-based path rejection from `servidor/rota.py`; enforce the data-model constraints verbatim: available instants are ISO-8601 with an explicit UTC offset; `ETD >= origin sunrise`, `ETD <= origin sunset`, `ETA <= destination sunset`, and `ETA >= ETD`; cache solar results per `(ICAO, UTC date)`, retry once at the next origin sunrise, record overnight there, and do not invent ground time or extra stops.
- [X] T016 [US3] Integrate the schedule into plan creation/update in `servidor/planos.py` and expose it by leg order in `servidor/planos_consulta.py`; persist JSON-safe UTC ISO-8601 strings under `PlanoDeVoo.resultado.programacao`, use `estado: "disponivel"` only for valid schedules and `estado: "indisponivel"` with `null` uncomputed times otherwise, and display legacy plans without that member as not calculated without inferring times.
- [X] T017 [P] [US3] Add per-leg ETD/ETA, applicable sunrise/sunset, deferred date, and overnight location to `templates/plano.html`; display an explicit unavailable state without calculating times in JavaScript.
- [X] T018 [P] [US3] Add the same saved per-leg schedule and overnight details to the tabular PDF in `servidor/pdf_plano.py` and `servidor/pdf_layout.py`.
- [X] T019 [US3] Update `specs/028-plano-diurno-tabular/quickstart.md` with `tests/test_catalogo_aerodromos.py` and `tests/test_programacao.py` in the focused pytest command and keep its solar boundary and legacy-plan scenarios aligned with the implementation.

**Checkpoint**: Every available schedule is reproducible from saved server
results; missing solar data never becomes a daylight-compliant schedule.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Align project guidance and complete final validation.

- [X] T020 [P] Update the Constitution version reference to `8.0.1` in `.cursor/rules/speckit-sdd.mdc` while preserving the active feature path `specs/028-plano-diurno-tabular/`.
- [X] T021 Remove the temporary Sync Impact Report HTML comment from `.specify/memory/constitution.md` before committing the amended Constitution.
- [ ] T022 Run the focused commands in `specs/028-plano-diurno-tabular/quickstart.md`, run `npm run css:build` to regenerate `static/css/tailwind.css`, and verify the map/report at 390 px and 1440 px without horizontal overflow or inaccessible controls.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No setup tasks; the existing stack is ready.
- **Foundational (Phase 2)**: No new foundation tasks; existing authentication,
  owner checks, persistence, and provider modules are reused.
- **User Stories (Phase 3+)**: Start after the existing project foundation.
  Recommended order is US1 → US2 → US3 because the stories update shared
  `templates/plano.html`, and later stories also extend shared serializers/PDF
  files. This is an integration/file-conflict order, not a new domain
  dependency.
- **Polish (Phase 6)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Independent after the existing application foundation.
- **US2 (P1)**: Independent in behavior; implement after US1 to avoid
  overlapping edits in `templates/plano.html`.
- **US3 (P1)**: Independent in behavior; implement after US2 because it extends
  the same template, plan serializer, and PDF pipeline.

### Within Each User Story

- Tests are added before their implementation tasks.
- WAC resolver and radar resolver tasks can run in parallel after their
  respective tests; the shared map template follows both.
- Report HTML and PDF tasks can run in parallel after the report view data is
  available.
- Solar parser, schedule algorithm, and presentation tests can be prepared in
  parallel; scheduling implementation follows the parser and algorithm
  contracts.
- HTML and PDF schedule rendering can run in parallel after the saved schedule
  is available.

### Parallel Opportunities

- **US1**: T001 with T002; then T003 with T004.
- **US2**: T006 with T007; then T009 with T010 after T008.
- **US3**: T011, T012, and T013; then T017 with T018 after T016.
- **Polish**: T020 and T021 can run in parallel because they update separate
  documentation files; T022 waits until all stories and both documentation
  updates are complete.

## Parallel Example: User Story 1

```text
Task T001: WAC selection tests in tests/test_tempo.py
Task T002: Unified radar/map tests in tests/test_tela_piloto.py

After both tests are ready:
Task T003: WAC selection in servidor/tempo.py
Task T004: Radar resolver in app.py

After T003 and T004:
Task T005: Unified map controls in templates/plano.html
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Implement and validate the single WAC and radar controls (US1).
2. Verify official PDF matching and automatic radar fallback before merging
   the map changes.
3. Stop and validate US1 independently before moving on.

### Incremental Delivery

1. US1 delivers a simplified, responsive map.
2. US2 adds the route-first tabular report and source provenance.
3. US3 adds the UTC daylight schedule and overnight reporting.
4. Complete cross-cutting CSS, browser, and quickstart validation.

## Notes

- `[P]` marks only tasks that can work on different files after prerequisites
  are met.
- Each task has a sequential ID, an exact file path, and a user-story label
  when it belongs to a story.
- No migration or dependency installation is planned.
- The temporary Constitution impact comment must be removed before commit.

## Phase 7: Convergence

- [ ] T023 Verify the report and map at 390 px and 1440 px in a live browser, including horizontal overflow and keyboard/touch operation, per SC-003 and FR-007 (partial).
