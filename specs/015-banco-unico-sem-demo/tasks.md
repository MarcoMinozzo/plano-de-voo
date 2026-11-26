# Tasks: Banco único e perfis sintéticos didáticos

**Input**: Design documents from `specs/015-banco-unico-sem-demo/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md` and `contracts/`

**Tests**: The specification includes independent test criteria and acceptance scenarios. Write focused tests first and verify that they fail before implementation.

**Organization**: Tasks are grouped by user story. All three stories are P1; US2 depends on imported profiles from US1, and US3 removes the legacy runtime after the new behavior is in place.

## Phase 1: Setup

**Purpose**: No new packages, services, or project scaffolding are needed.

## Phase 2: Foundational

**Purpose**: Resolve the contradictory agent rule before implementation so the constitution remains the governing policy.

- [X] T001 Align `.cursor/rules/speckit-sdd.mdc` with `.specify/memory/constitution.md` v6.0.0, removing the rule that synthetic proxies must remain in an isolated DEMO and the requirement to validate their aircraft data.

---

## Phase 3: User Story 1 - Consolidar os perfis existentes (Priority: P1)

**Goal**: Import exactly the twenty existing proxy profiles and their six technical values and units into the canonical product database, without writing to the legacy source.

**Independent Test**: Run the importer against two disposable databases; verify 20 profiles and all six values/units per profile, repeat without duplicates or changes, and confirm incomplete source or divergent destination data fails without partial writes.

### Tests for User Story 1

- [X] T002 [P] [US1] Add isolated source/destination database tests for exact profile count, all six values and units, idempotency, incomplete source, divergent conflicts, and unchanged source in `tests/test_importar_perfis_sinteticos.py`.

### Implementation for User Story 1

- [X] T003 [US1] Define the fixed identities and display labels for the twenty existing proxy profiles, without generating or validating technical values, in `servidor/perfis_sinteticos.py`.
- [X] T004 [US1] Implement the one-time importer in `servidor/importar_perfis_sinteticos.py`: read the source from `DATABASE_URL_DEMO_ORIGEM`, write to `DATABASE_URL`, require distinct PostgreSQL databases, select exactly the twenty proxy identities, copy all six technical values and their units and related source rows with remapped IDs, leave `extrato_id` null, and use a read-only source plus an atomic destination transaction.
- [X] T005 [US1] Make repeated imports a no-op for identical profiles and abort explicitly on missing profiles or divergent conflicts in `servidor/importar_perfis_sinteticos.py`; do not log either database URL or credentials.

**Checkpoint**: The profiles are safely importable into a disposable canonical database and the legacy database is unchanged.

---

## Phase 4: User Story 2 - Usar aeronaves sintéticas para fins didáticos (Priority: P1)

**Goal**: Offer the twenty proxies as a distinct didactic category, permit their use without factual-source validation, and clearly identify their limits in selection, results, and PDF.

**Independent Test**: With profiles present and RAB unavailable, verify that all twenty proxies remain selectable in a separate category, no generic profile is offered, a proxy can produce a didactic plan when ROTAER is available, and the screen and PDF identify synthetic, unvalidated values that do not represent the associated model.

### Tests for User Story 2

- [X] T006 [P] [US2] Add tests and the synthetic-profile test fixture for the separate category, visibility without RAB, absence of generic profiles, and the `/aeronaves` response in `tests/test_perfis_sinteticos.py`, `tests/test_tela_piloto.py`, and `tests/conftest_rota.py`.
- [X] T007 [P] [US2] Add tests that a proxy can be selected without synthetic-source validation and that the plan screen and PDF show the required non-operational warning in `tests/test_rota.py`, `tests/test_rota_pdf.py`, and `tests/test_proveniencia.py`.

### Implementation for User Story 2

- [X] T008 [US2] Separate factual models from didactic proxies in `servidor/catalogo.py`; keep factual models subject to RAB, completeness, and the existing 30-model limit, while returning the twenty proxies independently of RAB availability.
- [X] T009 [US2] Update `app.py` so `GET /aeronaves` exposes the factual catalogue and didactic profiles separately, includes the synthetic identity indicator, and does not expose `modo_demo` or make the didactic list depend on an environment mode.
- [X] T010 [US2] Update `servidor/proveniencia.py` and `servidor/planos.py` to permit the didactic proxies without treating their old range/reference metadata as validated applicability, while retaining each synthetic value and unit in plan results.
- [X] T011 [US2] Update `templates/plano_novo.html`, `templates/plano.html`, and `documentacao/piloto.md` to show a separate didactic category and the exact warning “perfil sintético didático — valores não validados; não representam dados do modelo associado”, alongside the existing no-real-flight/no-authorization notice.
- [X] T012 [US2] Update `servidor/pdf_plano.py` to render the synthetic/non-validated warning for proxy plans and their technical fields, without DEMO labels or any claim of applicability to the associated model.

**Checkpoint**: A proxy is available and clearly identified in selection, plan results, and PDF; factual catalogue and ROTAER behavior remain unchanged.

---

## Phase 5: User Story 3 - Operar sem modo DEMO (Priority: P1)

**Goal**: Make `DATABASE_URL` the only runtime and Alembic product database, while keeping tests isolated on `DATABASE_URL_TESTE` and removing obsolete DEMO workflows.

**Independent Test**: Verify app and Alembic resolve the same configured product database regardless of legacy DEMO variables; missing or invalid `DATABASE_URL` fails before a database session opens; tests continue to use only `DATABASE_URL_TESTE`.

### Tests for User Story 3

- [X] T013 [P] [US3] Add tests for one product database, explicit failure on missing or invalid `DATABASE_URL`, app startup failure before session configuration, Alembic URL selection, and test-database isolation in `tests/test_ambiente.py`.

### Implementation for User Story 3

- [X] T014 [US3] Remove database switching by `DEMO_MODE`, `APP_ENV`, and `DATABASE_URL_DEMO` from `servidor/ambiente.py`, `app.py`, and `alembic/env.py`; require and validate `DATABASE_URL` before configuring sessions or migrations.
- [X] T015 [US3] Keep test setup isolated to `DATABASE_URL_TESTE` and remove obsolete DEMO-mode setup from `tests/conftest.py`.
- [X] T016 [US3] Remove the obsolete synthetic generator and ROTAER-to-DEMO workflow from `servidor/semente_demo.py`, `servidor/perfis_demo.py`, and `servidor/importar_rotaer_demo.py`, plus their obsolete tests in `tests/test_semente_demo.py` and `tests/test_rotaer_demo.py`; retain the new profile identity registry and importer.
- [X] T017 [US3] Update `documentacao/operacao.md` with the single-database setup and the explicit, backed-up, one-time import procedure using `DATABASE_URL_DEMO_ORIGEM`; remove obsolete `DATABASE_URL_DEMO`, `DEMO_MODE`, and unused `APP_ENV` instructions.
- [X] T018 [US3] Remove remaining references to runtime DEMO behavior and verify all stories with the focused test command in `specs/015-banco-unico-sem-demo/quickstart.md`.

**Checkpoint**: Runtime and migrations use the canonical database only, tests remain isolated, and no obsolete DEMO command or environment switch remains.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No setup changes are required.
- **Foundational (Phase 2)**: T001 resolves the agent-rule conflict before implementation.
- **US1 (Phase 3)**: Depends on T001; required before US2 because it supplies the profiles to the canonical database.
- **US2 (Phase 4)**: Depends on US1; its catalog, plan, and PDF behavior uses the imported profiles.
- **US3 (Phase 5)**: Depends on US1 and US2; removes mode-based runtime paths after the new profile flow has been integrated.

### User Story Dependencies

- **US1 (P1)**: Can start after T001; no dependency on other user stories.
- **US2 (P1)**: Depends on US1 profile identities and imported records.
- **US3 (P1)**: Depends on the importer from US1 and the profile behavior from US2; its changes to `app.py` follow US2's API update.

### Parallel Opportunities

- T002 can be prepared independently from T001.
- T006 and T007 touch different test files and can be prepared in parallel.
- T013 can be prepared independently from US2 test work.
- Within US2, catalog/API, plan/provenance, templates, and PDF tasks touch separate implementation files after the tests are in place.

## Parallel Example: User Story 2

```text
Task: T006 — catalogue and API tests in tests/test_perfis_sinteticos.py and tests/test_tela_piloto.py
Task: T007 — plan and PDF tests in tests/test_rota.py and tests/test_rota_pdf.py
```

## Implementation Strategy

### MVP First

US1 is the first independently verifiable milestone: import the twenty existing records into disposable databases and prove preservation, repeatability, and non-destructive failure. The user-facing release requires all three P1 stories; stopping after US1 is not a complete product change.

### Incremental Delivery

1. Reconcile the agent rule and complete US1; validate import behavior on disposable databases only.
2. Complete US2; validate selection, plan, and PDF independently.
3. Complete US3; validate single-database runtime, isolated tests, documentation, and the full focused quickstart.

### Test Strategy

- Use disposable databases for importer tests and never point automated tests at the product or legacy databases.
- Verify source immutability and destination atomicity for both failure paths.
- Use the exact test selectors in `quickstart.md` after implementation; do not execute the real one-time import without explicit operator confirmation and a destination backup.
