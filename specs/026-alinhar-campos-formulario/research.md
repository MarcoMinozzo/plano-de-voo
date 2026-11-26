# Research: Alinhar campos do formulário

## Decision: Reuse the existing responsive grid utility

- **Decision**: Group each requested pair in a two-column responsive grid using the existing `sm:grid-cols-2` utility.
- **Rationale**: The same utility is already used in `templates/plano.html`, and the default `sm` breakpoint is 640 px. This satisfies the requested wider-screen pairing while keeping controls stacked on narrow screens.
- **Alternatives considered**: Add custom CSS or JavaScript for layout; rejected because existing responsive styles provide the required behavior without new dependencies or runtime logic.

## Decision: Preserve form controls and server behavior

- **Decision**: Move existing labels and inputs into layout-only wrappers; keep their names, values, constraints, and submission behavior unchanged.
- **Rationale**: The feature is presentation-only and the form already validates and processes these fields.
- **Alternatives considered**: Change form parsing or field validation; rejected as outside scope.
