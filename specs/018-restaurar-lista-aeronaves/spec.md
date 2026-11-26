# Feature Specification: Restore Synthetic Aircraft Selection

**Feature Branch**: `018-restaurar-lista-aeronaves`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Restore the list using the 20 already-defined test aircraft, show the correct aircraft name, and put calculation and educational-data disclaimers at the end of the input card and PDF report."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select a test aircraft by its correct name (Priority: P1)

A pilot creating a plan can find and select any of the twenty intended test aircraft by its correct model name, without generic source labels mixed into the option text. The form keeps the educational-data disclosure at the end of the input card.

**Why this priority**: Without selectable aircraft and recognizable names, the pilot cannot create a plan.

**Independent Test**: Open the new-plan form with the twenty profiles available and verify all intended names can be selected and the disclosure is shown at the end of the card.

**Acceptance Scenarios**:

1. **Given** the twenty test profiles are available, **When** the pilot opens the aircraft selector, **Then** all twenty intended model names appear, with no `DEMO` or `sintético` in the option names.
2. **Given** the test profiles are available, **When** the pilot views the input card, **Then** its ending disclosure states that calculations and profile data are educational, synthetic and unvalidated, do not represent the associated model, do not replace the manual, training, or current regulations, are unsuitable for real-flight planning, and do not authorize flight.

### User Story 2 - Preserve and understand the report's educational data (Priority: P1)

A pilot can review a plan and its PDF with the selected model clearly named and the educational-data limitations disclosed at the end of the report.

**Why this priority**: The synthetic values must not be mistaken for validated aircraft specifications or operational guidance.

**Independent Test**: Generate a plan with a test profile and verify the model name, synthetic field identification, units, and end-of-report disclaimer in the PDF.

**Acceptance Scenarios**:

1. **Given** a plan uses a test profile, **When** the pilot views its result and PDF, **Then** the correct model name is shown and synthetic values remain identified with their units.
2. **Given** the PDF is rendered, **When** the pilot reaches its end, **Then** the disclaimer states that calculations and profile values are educational, synthetic and unvalidated, do not represent the associated model, do not replace the manual, training, or current regulations, are not for real-flight planning, and do not authorize flight.

### User Story 3 - Keep the existing profiles intact (Priority: P1)

The application operator can make the twenty already-defined profiles available without changing their values or the existing product data.

**Why this priority**: The list depends on preserving the existing educational profiles without duplicating or damaging product data.

**Independent Test**: Import from the available legacy source into the existing product store, compare all six values and units per profile, repeat the import, and verify the source and unrelated records remain unchanged.

**Acceptance Scenarios**:

1. **Given** the source contains all twenty complete profiles, **When** they are made available, **Then** each profile is associated with its intended model and retains all six values and units.
2. **Given** profiles have already been made available, **When** the same operation is repeated, **Then** no duplicates or value changes occur.
3. **Given** a profile is missing or conflicts with an existing record, **When** the operation runs, **Then** it reports the issue and makes no partial changes.

### Edge Cases

- The source has fewer or more than twenty profiles, a missing technical value or unit, or multiple selected values for one field.
- A destination profile exists with identical or conflicting values.
- The source cannot be read or the destination backup cannot be verified.
- The factual aircraft catalogue is unavailable while the synthetic profiles remain present.
- A generated report has no synthetic profile; ordinary factual-aircraft disclosures remain unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST offer the twenty intended test profiles separately from factual aircraft, and each selectable option MUST show only the correct associated model name.
- **FR-002**: The system MUST preserve the six existing technical values and their units for every profile; it MUST NOT generate, recalculate, or research replacement values.
- **FR-003**: The system MUST associate source profiles numbered 01 through 20 with the twenty already-defined models in their established order.
- **FR-004**: The system MUST leave the legacy source unchanged and MUST NOT transfer pilots, plans, generic aircraft, or factual catalogue data from that source.
- **FR-005**: Making profiles available MUST be repeatable without duplicates or changes to identical existing records. Missing, incomplete, or conflicting data MUST result in an explicit failure with no partial writes.
- **FR-006**: The input card MUST end with one disclosure stating that calculations and profile data are educational, synthetic and unvalidated, do not represent the associated model, do not replace the manual, training, or current regulations, are unsuitable for real-flight planning, and do not authorize flight.
- **FR-007**: A plan using a test profile MUST identify synthetic values and units in its results and PDF. The PDF MUST end with a disclosure stating that calculations and profile values are educational, synthetic and unvalidated, do not represent the associated model, do not replace the manual, training, or current regulations, are unsuitable for real-flight planning, and do not authorize flight.
- **FR-008**: The application MUST continue using one product data store; making the profiles available MUST NOT create a second product store or modify unrelated factual records.

### Key Entities *(include if feature involves data)*

- **Test aircraft profile**: One of twenty existing educational profiles, associated with a model name and containing six synthetic technical values with units.
- **Synthetic technical value**: A preserved profile value with its unit and synthetic origin, not a validated specification for the associated model.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 20 intended profiles are selectable by their correct model names, with zero generic or synthetic labels in the option text.
- **SC-002**: 100% of the six existing technical values and units are preserved for all 20 profiles.
- **SC-003**: A repeated operation creates zero duplicates; incomplete or conflicting input results in zero partial changes, and the source remains unchanged.
- **SC-004**: Every relevant input card and PDF clearly identifies synthetic data; the PDF disclosure appears at the end of the report.
- **SC-005**: The application continues using exactly one product data store, with no pilots, plans, or factual catalogue records copied from the source.

## Assumptions

- The twenty intended model names and their order are already defined by the project.
- The legacy source's numbered profiles 01–20 have no direct model association; ordinal mapping to the established model order is the approved mapping.
- Existing result and PDF disclosures for factual aircraft remain unchanged.
- A verified backup of the existing product data is required before the one-time production import.
