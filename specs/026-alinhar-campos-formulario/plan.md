# Implementation Plan: Alinhar campos do formulário

**Branch**: `026-alinhar-campos-formulario` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/026-alinhar-campos-formulario/spec.md`

## Summary

Reorganize the new-plan form so date/time and passenger count share a row, and passenger weight and baggage weight share another row. Reuse the existing responsive two-column utility at the 640 px breakpoint; preserve current field names, values, validation, and server behavior.

## Technical Context

**Language/Version**: Python 3.10+ and existing Jinja templates.

**Primary Dependencies**: Existing Flask/Jinja application and compiled Tailwind CSS; no new dependencies.

**Storage**: No changes.

**Testing**: Focused pytest integration test in `tests/test_tela_piloto.py`.

**Target Platform**: Existing web application in supported browsers.

**Project Type**: Server-rendered web application.

**Performance Goals**: No new runtime work or network requests.

**Constraints**: Keep the date confirmation control with its related date field; preserve labels, field names, values, validation, and form submission.

**Scale/Scope**: One template and one focused rendering test.

## Constitution Check

| Principle | Status | Evidence |
|---|---|---|
| I. Specification before code | PASS | Feature 026 has a spec, plan, and tasks before editing the form template. |
| II. Educational boundary | PASS | The existing educational notice is unchanged. |
| III. Calculation in the server | PASS | Only field layout changes; all data and calculations remain unchanged. |
| IV. Units and source explicit | PASS | Existing weight labels retain their kg units. |
| V. Small stack and relational database | PASS | No new dependency, storage, route, or database change. |

No constitutional violation identified.

## Project Structure

### Documentation (this feature)

```text
specs/026-alinhar-campos-formulario/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── formulario-plano.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
templates/plano_novo.html      # Group the requested form fields responsively
tests/test_tela_piloto.py      # Verify responsive row groups and unchanged field names
static/css/tailwind.css        # Existing compiled responsive utility; no CSS change expected
```

**Structure Decision**: Keep the change in the existing server-rendered form. Reuse the responsive `sm:grid-cols-2` utility already used by the plan details template, and keep the date confirmation control nested with the date field.

## Phase 0: Outline & Research

- The form is in `templates/plano_novo.html`; all four requested controls already have stable names and server-side validation.
- `templates/plano.html` already uses `sm:grid-cols-2`, so no new breakpoint or stylesheet dependency is needed.
- The default `sm` breakpoint provides the requested two-column layout at 640 px and stacks the columns below that width.
- No external research or dependency decision is needed for this presentation-only change.

## Phase 1: Design & Contracts

- `data-model.md` records that no entity, field, or persistence changes are required.
- `contracts/formulario-plano.md` defines the desktop pairing and narrow-screen behavior.
- `quickstart.md` describes the focused regression test and responsive browser check.
- Post-design Constitution Check: PASS. Form submission, units, validation, and educational notices remain unchanged.

## Complexity Tracking

No violations or additional abstractions to justify.
