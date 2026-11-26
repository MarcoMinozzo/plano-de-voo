# Implementation Plan: Enxugar informações da página do plano

**Branch**: `025-enxugar-pagina-plano` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/025-enxugar-pagina-plano/spec.md`

## Summary

Simplify the flight-plan detail page by removing its status label, verbose synthetic-profile warning and target, scale-refueling note, and technical-provenance table. Keep aircraft identity, route data, reasons and alerts, the general educational notice, stored results, and PDF output unchanged.

## Technical Context

**Language/Version**: Python 3.10+ and existing Jinja templates.

**Primary Dependencies**: Existing Flask/Jinja stack; no new dependencies.

**Storage**: No changes to PostgreSQL or persisted plan results.

**Testing**: Focused pytest regression in `tests/test_rota_pdf.py`; verify the page output and unchanged PDF content.

**Target Platform**: Existing Linux Flask application.

**Project Type**: Server-rendered web application.

**Performance Goals**: No new requests, rendering steps, or runtime work.

**Constraints**: Modify only the plan-page presentation. Preserve the general educational/non-authorization notice, reasons and alerts, calculation results, stored provenance, and PDF.

**Scale/Scope**: One orientation helper, its plan-page call site, one template, and the existing regression test.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| I. Specification before code | PASS | Feature 025 has a spec, plan, and tasks before template changes. |
| II. Educational boundary | PASS | The general notice that the product is didactic and does not authorize flight remains visible; PDF disclosure is unchanged. |
| III. Calculation in the server | PASS | This is presentation-only; no calculations or client-side formulas change. |
| IV. Units and source explicit | PASS | The detailed provenance table is removed from this screen under the amended page-specific exception; any technical synthetic value still displayed individually remains identified with its unit. |
| V. Small stack and relational database | PASS | No dependency, storage, route, or database change. |
| Pilot access and documentation | PASS | Authentication, ownership, and pilot documentation are unchanged. |

No constitutional violation identified.

## Project Structure

### Documentation (this feature)

```text
specs/025-enxugar-pagina-plano/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── pagina-plano.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
servidor/pdf_plano.py      # Provide page-specific orientation without the synthetic-profile subsection
app.py                     # Use page-specific orientation only for plan details
templates/plano.html       # Remove only the specified repeated/detail sections
tests/test_rota_pdf.py     # Assert page cleanup and unchanged PDF disclosure
```

**Structure Decision**: Keep the presentation change in the existing server-rendered plan flow. The page-specific orientation helper prevents synthetic-profile copy from reappearing inside the expandable guidance, while plan creation and PDF continue using the complete source. The test reuses the existing synthetic-profile plan scenario to guard page/PDF separation.

## Phase 0: Outline & Research

- The current plan page renders status, synthetic-profile disclosure, exercise target, refueling hypothesis, technical provenance, and the full pilot guide directly from existing data.
- Existing PDF generation consumes the same stored result separately; leave it and all stored fields unchanged.
- The pilot guide is shared with plan creation and PDF, so only the plan-detail page receives a filtered copy with the synthetic-profile subsection omitted.
- No external research or dependency decision is needed for this presentation-only change.

## Phase 1: Design & Contracts

- `data-model.md` records that no entity, field, or persistence changes are required.
- `contracts/pagina-plano.md` defines the sections removed and content that must remain.
- `quickstart.md` describes the focused regression test and manual page check.
- Post-design Constitution Check: PASS. The amended constitution permits omitting the verbose profile disclosure and provenance table on this page while retaining the general educational notice and preserving PDF disclosures.

## Complexity Tracking

No violations or additional abstractions to justify.
