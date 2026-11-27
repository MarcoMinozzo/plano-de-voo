# Tasks: METAR regional próximo ao aeródromo

**Input**: Design documents from `specs/029-metar-regional/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/meteorologia-relatorio.md`

**Tests**: Incluídos porque a especificação define cenários de teste independentes e critérios de aceitação.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup

**Purpose**: Reutilizar o ambiente Flask, pytest e dependências existentes. Não há inicialização de projeto nem dependências novas.

## Phase 2: Foundational

**Purpose**: Não há infraestrutura compartilhada ou migração necessária; os dados continuam no JSON meteorológico atual.

---

## Phase 3: User Story 1 - Consultar meteorologia local ou regional (Priority: P1) 🎯 MVP

**Goal**: Preferir METAR do aeródromo; sem ele, selecionar um METAR AWC a até 50 NM e identificá-lo como regional, sem impedir a consulta independente do TAF.

**Independent Test**: Simular METAR direto, METAR regional elegível, limite de 50 NM, estação além do limite, TAF sem METAR e falha isolada de cada produto. Confirmar identificação regional em HTML, fontes e PDF.

### Tests for User Story 1

- [X] T001 [P] [US1] Add service regression cases for direct METAR priority, nearest eligible station, 50 NM boundary, tie-breaking, invalid coordinates, beyond-limit stations, independent TAF, and isolated provider failures in `tests/test_tempo.py`
- [X] T002 [P] [US1] Add HTML regression coverage for regional station identity, distance, UTC time, and TAF visibility without METAR in `tests/test_tela_piloto.py`
- [X] T003 [P] [US1] Add PDF regression coverage for regional METAR attribution and regional source identity in `tests/test_rota_pdf.py`

### Implementation for User Story 1

- [X] T004 [US1] Separate METAR and TAF request/error handling, retain per-product availability, and log provider failures without credentials in `servidor/tempo.py`
- [X] T005 [US1] Add AWC bounding-box lookup, exact great-circle distance filtering at 50 NM, deterministic nearest-station selection, and regional station metadata in `servidor/tempo.py`
- [X] T006 [P] [US1] Render regional label, station name/ICAO, distance, and UTC observation time without implying airport conditions in `templates/plano.html`
- [X] T007 [P] [US1] Preserve METAR publishing-station identity and AWC attribution in the report source rows in `servidor/planos_consulta.py`
- [X] T008 [P] [US1] Verify PDF assembly renders regional METAR identity through the existing shared bulletin and source-table flow in `servidor/pdf_plano.py` and `servidor/pdf_layout.py`
- [X] T009 [US1] Document the meaning and limits of a regional METAR and independent TAF in `documentacao/piloto.md`

**Checkpoint**: A saved plan independently displays the closest eligible METAR as regional, keeps TAF tied to the requested aerodrome, and reports unavailable products without fabricated values.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete change against the documented scenarios.

- [X] T010 Run the focused regression command and verify every scenario in `specs/029-metar-regional/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No changes required; existing project environment is reused.
- **Foundational (Phase 2)**: No changes required; no migration or shared infrastructure is needed.
- **User Story 1 (Phase 3)**: Independent after the existing project setup; all user-facing behavior belongs to this single story.
- **Polish (Phase 4)**: Depends on all User Story 1 implementation tasks.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on another story.

### Within User Story 1

- T001, T002, and T003 are independent test-file changes and should be written before implementation.
- T004 and T005 both modify `servidor/tempo.py`; complete T004 before T005.
- T006, T007, and T008 depend on the service metadata contract from T004-T005 and can then proceed in parallel in separate files.
- T009 updates pilot documentation after the meaning of the regional result is implemented.
- T010 runs after all implementation and regression work.

### Parallel Opportunities

- T001, T002, and T003 can run in parallel because they touch separate test files.
- After T004-T005 establish the service result shape, T006, T007, and T008 can run in parallel because they touch separate presentation/source files.

## Parallel Example: User Story 1

```text
Before implementation:
Task: T001 service regression tests in tests/test_tempo.py
Task: T002 HTML regression tests in tests/test_tela_piloto.py
Task: T003 PDF regression tests in tests/test_rota_pdf.py

After the service metadata is established:
Task: T006 HTML rendering in templates/plano.html
Task: T007 source attribution in servidor/planos_consulta.py
Task: T008 PDF rendering in servidor/pdf_plano.py and servidor/pdf_layout.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Reuse the current test/runtime setup; no setup or foundational code changes are needed.
2. Add service, HTML, and PDF regressions.
3. Implement independent product handling and the regional METAR fallback.
4. Update HTML, source attribution, and PDF presentation.
5. Run the focused quickstart validation and verify each acceptance scenario.

### Incremental Delivery

User Story 1 is the complete MVP. Ship it only when the direct/regional selection, 50 NM cutoff, independent TAF, diagnostic logging, and HTML/PDF attribution all pass.

## Notes

- `[P]` tasks operate on different files and have no dependency on unfinished work.
- Keep the requested aerodrome separate from the station that actually published a regional METAR.
- Do not add a TAF regional fallback or persist read-only weather refreshes made when opening a saved plan.
