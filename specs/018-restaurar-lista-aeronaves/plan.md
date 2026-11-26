# Implementation Plan: Restore Synthetic Aircraft Selection

**Branch**: `018-restaurar-lista-aeronaves` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/018-restaurar-lista-aeronaves/spec.md`

## Summary

Restore the twenty already-defined educational aircraft profiles by importing the numbered legacy records in their approved order, preserving all six values and units. Display only each target model's correct name in the selector, keep the input-card disclaimer at the card's end, and place the synthetic-profile disclaimer at the end of the PDF.

The legacy source is at revision `c8d3f41a2b67`; its generic names and older `fonte_tecnica_aeronave` schema do not match the current importer assumptions. Read the legacy schema without modifying it, map records by ordinal, and retain the existing single product database and atomic import protections.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: Flask, SQLAlchemy 2, psycopg 3, Alembic, ReportLab; no new dependencies.

**Storage**: PostgreSQL 16 for product data; isolated test database and SQLite fixtures for unit coverage.

**Testing**: pytest; focused importer, catalogue, input-screen, plan/PDF tests.

**Target Platform**: Linux Flask server and browser.

**Project Type**: Server-rendered Flask web application with JSON catalogue endpoint and server-generated PDF.

**Performance Goals**: No new latency target; the feature handles exactly twenty profiles.

**Constraints**: Preserve all six existing technical values and units per profile. Keep the legacy source read-only and the product store singular. Back up the product store before the one-time import. Do not copy pilots, plans, generic aircraft, or factual catalogue data. Never present synthetic values as validated data for the target model. Show the correct model name in the option; put the input disclaimer at the end of the input card and the report disclaimer at the end of the PDF.

**Scale/Scope**: Twenty profiles; one existing product store and one legacy read-only source for the one-time import; no schema migration or new service.

## Constitution Check

- **I. Specification before code**: Pass. This feature has an approved specification, this plan, and will have tasks before application code changes.
- **II. Educational boundary**: Pass. The input card and PDF retain explicit synthetic/non-operational disclosures; the target model name is not presented as validated applicability.
- **III. Server-side calculations and PDF**: Pass. No calculation moves to the browser; the PDF remains server-generated.
- **IV. Units and provenance**: Pass. Preserve the six values and units, identify each synthetic field, and do not invent publisher/date provenance or claim model applicability.
- **V. Single relational product store**: Pass. Use the existing PostgreSQL product store and isolated tests, with no new dependencies or database.
- **Safe import**: Pass. Read the source in read-only mode; validate before destination writes; use one atomic destination transaction; require a verified backup before production import; abort on incomplete source or conflicting destination data.

**Gate**: Approved. No unresolved clarification or constitutional exception.

## Phase 0: Research

See [research.md](research.md). The current ORM importer cannot safely read the legacy source through the latest `FonteTecnicaAeronave` mapping because the source predates six nullable provenance columns. Use SQLAlchemy Core reflection and select only the legacy columns required for the import; do not upgrade or otherwise modify the source.

## Phase 1: Design

See [data-model.md](data-model.md), [contracts/selection-and-report.md](contracts/selection-and-report.md), [contracts/import.md](contracts/import.md), and [quickstart.md](quickstart.md).

## Project Structure

### Documentation (this feature)

```text
specs/018-restaurar-lista-aeronaves/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── selection-and-report.md
│   └── import.md
└── tasks.md
```

### Source Code (repository root)

```text
servidor/
├── importar_perfis_sinteticos.py
├── planos.py
├── perfis_sinteticos.py
└── pdf_plano.py
templates/
└── plano_novo.html
tests/
├── test_importar_perfis_sinteticos.py
├── test_perfis_sinteticos.py
├── test_rota.py
├── test_tela_piloto.py
└── test_rota_pdf.py
documentacao/
└── operacao.md
```

**Structure Decision**: Extend the existing Flask application and one-time importer. No new application package, database schema, or runtime service is needed. Keep factual catalogue filtering and ordinary factual-aircraft disclosures unchanged.

## Complexity Tracking

No constitution violations or additional project structures.
