# Data Model: Restore Synthetic Aircraft Selection

## Existing Entities

### Synthetic Aircraft Profile

Represents one of the twenty educational profiles stored in the product aircraft catalogue.

| Attribute | Meaning | Validation |
|---|---|---|
| Display name | Correct target aircraft model name | Matches one of the twenty fixed profile identities |
| Profile status | Identifies this record as synthetic | Must remain `proxy_sintetico`; must not be a factual RAB record |
| Factual catalogue reference | Link to a factual RAB extract | Must be empty for these profiles |
| Technical values | Empty weight, maximum takeoff weight, baggage limit, usable fuel, cruise speed, and cruise consumption | All six values must exist and be copied unchanged |
| Technical units | Units for each stored value | Must be copied unchanged with the associated values |

### Synthetic Technical Source

Represents a selected source row for one of the six technical fields belonging to a profile.

| Attribute | Meaning | Validation |
|---|---|---|
| Profile | Aircraft profile owning the source row | Must reference exactly one profile |
| Field | One of the six technical fields | Exactly one selected synthetic source per required field |
| Value and unit | Existing educational value and unit | Both must be present and preserved |
| Source type | Indicates synthetic origin | Must be `sintetica` and selected |
| Target model context | Model chosen as the exercise label | Must not imply the value is validated or applicable to that model |

## Relationships and Mapping

- One synthetic aircraft profile has exactly six selected synthetic technical sources.
- Legacy aircraft rows named `Aeronave DEMO 01` through `Aeronave DEMO 20` map by ordinal position to the fixed target-model order in `servidor/perfis_sinteticos.py`.
- The legacy source is read-only. Source IDs are not reused as product IDs; destination source rows reference the new product profile.
- The product schema does not change. Missing optional provenance columns in the old source are represented as absent/null destination metadata, never invented values.

## Import Validation and State

- Validate the exact twenty source identities, all six fields, one selected source per field, non-null value and unit, and required aircraft technical values before starting destination writes.
- An identical destination profile is `already present`; it is not rewritten.
- A divergent destination profile is a conflict; abort the full transaction without overwriting existing records.
- On success, the product profile is available in the synthetic catalogue independently of factual RAB catalogue availability.
