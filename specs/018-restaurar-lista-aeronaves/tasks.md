# Tasks: Restore Synthetic Aircraft Selection

**Input**: Design documents from `specs/018-restaurar-lista-aeronaves/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`

**Tests**: Focused tests are included for changed selection, PDF, and import behavior.

**Organization**: Tasks are grouped by user story. User Story 3 depends on the target-name registry from User Story 1.

## Phase 1: Setup

**Purpose**: No packages, services, or project scaffolding are needed.

## Phase 2: Foundational

**Purpose**: No shared blocking code changes are required; the current application, test isolation, and database configuration are reused.

---

## Phase 3: User Story 1 - Select a test aircraft by its correct name (Priority: P1)

**Goal**: Show the twenty target model names without source labels and put one complete educational disclaimer at the end of the input card.

**Independent Test**: With test profiles available, verify the selector has twenty model-only options and the card-ending disclaimer includes all required synthetic and non-operational limits.

### Tests for User Story 1

- [X] T001 [P] [US1] Assert the twenty model-only option names, correct proxy target name, and the single end-of-card disclaimer in `tests/test_perfis_sinteticos.py`, `tests/test_tela_piloto.py`, and `tests/test_rota.py`.

### Implementation for User Story 1

- [X] T002 [US1] Update `nome_origem` to the legacy numbered identities and `nome_exibicao` to the exact target model name for all twenty profiles in `servidor/perfis_sinteticos.py`; derive proxy `modelo_alvo` directly from the model-only aircraft name in `servidor/planos.py`.
- [X] T003 [US1] Keep option text model-only and move the synthetic and educational-limit text into one final disclaimer at the end of the input card in `templates/plano_novo.html`.

**Checkpoint**: All twenty profiles render with the correct names, without `DEMO` or `sintético` in option text; the input-card disclaimer is the final card content.

---

## Phase 4: User Story 2 - Preserve and understand the report's educational data (Priority: P1)

**Goal**: Keep per-field synthetic labels and units and end each synthetic-profile PDF with the complete educational disclaimer.

**Independent Test**: Generate a synthetic-profile report and verify the disclaimer is the final report content, after existing pilot guidance.

### Tests for User Story 2

- [X] T004 [P] [US2] Add a focused assertion that synthetic PDF content ends with the full disclaimer after pilot guidance in `tests/test_rota_pdf.py`.

### Implementation for User Story 2

- [X] T005 [US2] Append the complete synthetic and non-operational disclaimer after the pilot guidance for synthetic-profile reports in `servidor/pdf_plano.py`, preserving per-field synthetic labels and units.

**Checkpoint**: Synthetic-profile PDFs retain field provenance and units and end with the required disclaimer; factual-aircraft PDFs remain unchanged.

---

## Phase 5: User Story 3 - Keep the existing profiles intact (Priority: P1)

**Goal**: Import exactly the twenty existing legacy profiles into the canonical product database, with unchanged values and units, no source changes, and no duplicates.

**Independent Test**: Use a legacy-schema fixture representing revision `c8d3f41a2b67`; verify all twenty ordinal mappings, 120 selected source rows, values/units, read-only source, idempotency, and atomic failure.

### Tests for User Story 3

- [X] T006 [P] [US3] Build legacy source tables without the six `d1e2f3a4b5c6` columns and test ordinal mapping, all six values/units, same-name factual records, repeat imports, missing/duplicate fields, divergent conflicts, and source immutability in `tests/test_importar_perfis_sinteticos.py`.

### Implementation for User Story 3

- [X] T007 [US3] Read and validate legacy `aeronave` and `fonte_tecnica_aeronave` rows using SQLAlchemy Core reflection, map numbered profiles to the target registry, distinguish synthetic profiles from factual records with the same model name, and keep the read-only source plus atomic destination transaction in `servidor/importar_perfis_sinteticos.py`.
- [X] T008 [US3] Document the old-schema read-only source, approved ordinal mapping, required backup, and non-imported records in `documentacao/operacao.md`.
- [X] T009 [US3] Verify a restorable backup of the existing product database, run the one-time importer from `servidor/importar_perfis_sinteticos.py`, and confirm twenty profiles are available without changing the source or duplicating product data.

**Checkpoint**: The product database contains the twenty target-named synthetic profiles and the legacy source remains unchanged.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify all user-visible outcomes and regression boundaries.

- [X] T010 Run the focused pytest command and manual scenarios in `specs/018-restaurar-lista-aeronaves/quickstart.md`; verify factual catalogue behavior, single product database, selector, plan results, and final PDF disclaimer.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No setup changes required.
- **Foundational (Phase 2)**: No blocking changes required.
- **User Stories (Phase 3+)**: US1 and US2 are independent; US3 depends on the target identities from US1.
- **Polish (Phase 6)**: Depends on all three user stories and the production import validation.

### User Story Dependencies

- **User Story 1 (P1)**: Independent; establishes the fixed source identities and target display names.
- **User Story 2 (P1)**: Independent; the PDF disclaimer can be tested using existing synthetic plan fixtures.
- **User Story 3 (P1)**: Depends on T002 because the importer uses the fixed source and target identities.

### Parallel Opportunities

- T001 and T004 touch separate test files and can be prepared in parallel.
- After T001 fails, T002 and T003 touch separate implementation files and can be implemented in parallel.
- T006 can be prepared after T002 while US2 work proceeds because it changes only the importer test file.
- T008 documentation can be updated independently of the importer implementation; T009 must wait for T007, T008, and passing focused tests.

## Parallel Example: User Story 1 and User Story 2

```text
Task: T001 — selection and input-card tests in tests/test_perfis_sinteticos.py and tests/test_tela_piloto.py
Task: T004 — PDF end-disclaimer test in tests/test_rota_pdf.py
```

## Implementation Strategy

### MVP First

The visible selector change in US1 is independently testable with fixtures, but the reported empty product list is not fixed until US3 imports the profiles. The smallest usable outcome is US1 plus US3; US2 is required before release to place the disclaimer at the end of the PDF.

### Incremental Delivery

1. Implement and verify the selector names and input-card disclaimer.
2. Implement and verify the final PDF disclaimer without changing factual-aircraft reports.
3. Implement and test the legacy-schema import, update operation documentation, create a verified backup, and import into the existing product database.
4. Run the focused test suite and the complete quickstart checks.

### Validation Strategy

- Tests use isolated SQLite/PostgreSQL test databases, never product or legacy databases.
- The legacy source fixture matches the old schema and proves missing optional columns are not queried.
- Verify destination atomicity and source immutability for both success and failure scenarios.
- Do not run the real import before tests pass and a restorable product backup is confirmed.
