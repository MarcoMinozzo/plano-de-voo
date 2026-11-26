# Contract: One-Time Profile Import

## Preconditions

- The product database is the existing canonical database configured for the application.
- The legacy source is a distinct PostgreSQL database at revision `c8d3f41a2b67`; it is read-only and is never upgraded or modified.
- A verified backup of the product database exists before the production import.
- The source contains exactly twenty numbered generic profiles, each with six selected synthetic values and units.

## Behavior

- The import maps source profile 01 to the first established target model and continues by ordinal through profile 20.
- All twenty profiles and their six values/units are validated before any destination write.
- Insert all missing profiles and provenance rows in one atomic destination transaction.
- Repeated import of identical profiles is a no-op; differing values for an existing target are a conflict.
- An existing factual aircraft with the same model name is not a synthetic-profile conflict and must remain unchanged.
- Never copy pilots, plans, generic source aircraft, RAB extracts, aerodromes, or factual catalogue records.
- Never modify the source; never print database URLs, credentials, or profile values to logs.

## Outcomes

- Success reports only aggregate counts: newly imported and already present profiles.
- Missing, extra, incomplete, duplicate, or conflicting data fails explicitly and leaves the destination unchanged by that attempt.
- No second product database or runtime fallback is created.
