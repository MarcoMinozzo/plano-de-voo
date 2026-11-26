# Research: Restore Synthetic Aircraft Selection

## Legacy Source Compatibility

**Decision**: Read the legacy `aeronave` and `fonte_tecnica_aeronave` tables through SQLAlchemy Core reflection, validate the required legacy columns, and select only those columns. Convert selected source rows to the current destination model after validating all profiles.

**Rationale**: The source is at Alembic revision `c8d3f41a2b67`. The next revision, `d1e2f3a4b5c6`, adds six nullable provenance fields (`limite_inferior`, `limite_superior`, `metodo_geracao`, `versao_semente`, `incerteza`, and `justificativa_comparabilidade`). The current ORM maps those fields, so loading source provenance rows through the full current ORM selection requires columns absent in the legacy schema.

**Alternatives considered**:
- Upgrade the source to the current schema: rejected because the source must remain unchanged.
- Read all source rows with the current ORM: rejected because the source schema lacks mapped columns and the ORM query can fail.
- Add a new package or copy source data to another database: rejected because no new dependency or product database is allowed.

## Profile Identity and Mapping

**Decision**: Match source records `Aeronave DEMO 01` through `Aeronave DEMO 20` to the twenty existing target models by ordinal position in `PERFIS_SINTETICOS`. Set the product aircraft display name to the target model name and keep the synthetic status and provenance separate from that name.

**Rationale**: The legacy records are generic and carry no target-model association. The user approved using the stable existing model order for the 01-to-20 mapping. The profile registry already holds the intended target order.

Destination identity is the combination of target model name and synthetic profile state. A factual aircraft may already use the same model name; it is not an import conflict and must remain unchanged.

**Alternatives considered**:
- Infer associations from numeric values or metadata: rejected; the source does not establish such a relationship.
- Keep generic source names in the product selector: rejected; the user requires correct model names.
- Validate or replace values against aircraft manuals: rejected; these are existing educational values, not factual specifications.

## Import Safety

**Decision**: Retain the current safeguards: require distinct PostgreSQL source and destination URLs, set the source transaction read-only, validate all twenty profiles and six selected synthetic values/units before writing, and insert through one destination transaction. Treat identical destination profiles as already imported and abort on divergent conflicts.

**Rationale**: This preserves the single product database, source immutability, repeatability, and all-or-nothing behavior required by the specification.

**Alternatives considered**:
- Write profiles individually as they are read: rejected because late validation failures could leave partial imports.
- Use a second production staging database: rejected by the single-product-store requirement.

## Disclaimer Placement

**Decision**: Combine the existing profile warning and educational limitation into one note at the end of the input card. Append the synthetic-profile disclaimer after the pilot guidance at the end of the PDF, while retaining per-field synthetic labels and units.

**Rationale**: The user specified both locations. Current `plano_novo.html` places two synthetic notes directly below the selector, and `pdf_plano.py` adds pilot guidance after the main report, so the final synthetic disclaimer must be appended after that guidance to be genuinely last.

**Alternatives considered**:
- Put the PDF disclaimer in the technical provenance section: rejected because it would not be at the end of the report.
- Remove per-field labels: rejected because the constitution requires synthetic identity and units to remain visible throughout results and PDF.
