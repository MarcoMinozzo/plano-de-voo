# Research: Tela do plano organizada por trecho

## METAR source fields

**Decision**: Use the existing AviationWeather.gov JSON request and preserve `rawOb`, `reportTime`, and only the structured observation fields actually returned. Present those fields with Portuguese labels and their documented units. The raw METAR remains available unchanged. Do not parse missing data from raw text or translate unsupported groups as facts.

**Rationale**: The official AviationWeather.gov API describes `/api/data/metar` as decoded aviation observations and publishes a JSON schema. The schema documents fields including temperature (`temp`, Celsius), dew point (`dewp`, Celsius), wind direction (`wdir`, degrees or `VRB`), wind speed and gust (`wspd`/`wgst`, knots), visibility (`visib`, statute miles), altimeter setting (`altim`, hPa), present-weather code (`wxString`), vertical visibility (`vertVis`, feet), cloud layers (`clouds`), report type, timestamp, and original text (`rawOb`). Using these provider fields avoids reinterpreting a bulletin or introducing a METAR parsing dependency.

**Alternatives considered**:

- Parse every raw METAR group in application code: rejected because partial parsing could silently misstate a group and would duplicate a standards parser.
- Replace the raw report with a translated paragraph: rejected because the pilot must be able to inspect the original source text.
- Add a third-party METAR parser: rejected because the provider already supplies structured observation fields and adding a dependency is unnecessary for this scope.

Source: [AviationWeather.gov Data API](https://aviationweather.gov/data/api/) and its [OpenAPI schema](https://aviationweather.gov/data/schema/openapi.yaml), `/api/data/metar` and `METARproperties`.

## Intermediate aerodrome weather

**Decision**: Capture METAR/TAF once for each distinct aerodrome in the calculated route while the plan is prepared. Retain the existing `origem` and `destino` snapshot keys used by PDF generation, and add an ICAO-keyed collection for every route aerodrome so each leg can display its own departure and arrival.

**Rationale**: The current plan snapshot contains weather only for the overall origin and destination. Multi-leg fichas must show the actual stop's weather; fetching on tab changes would add network traffic and make the result vary while reading the same saved plan.

**Alternatives considered**:

- Reuse overall origin/destination METAR for intermediate legs: rejected because it would show the wrong aerodrome's report.
- Query AWC when the pilot selects a tab: rejected because tab navigation should not make external requests.

## Map and route presentation

**Decision**: Derive one coordinate pair for each persisted leg in the existing plan view and update the displayed map from the selected leg. Keep all route calculations and point selection server-owned.

**Rationale**: `app.py` currently builds a route-wide `pontos` array, while the approved `EXPERIENCE.md` calls for a map in each leg ficha and one selected ficha at a time. Per-leg endpoints can be derived from the already-persisted route without changing calculation or persistence.

**Alternatives considered**:

- Recalculate the route when a tab changes: rejected; the tab is presentation state only.
- Keep drawing every leg and highlight the selected one: rejected because it would not limit the map to the active leg.

## Map source availability

**Decision**: Preserve streets as the initial base, keep OpenAIP separate and subject to its existing license/key/attribution requirements, and expose WAC as unavailable until feature 009's validation gates are evidenced. Radar remains independently controlled and initially off.

**Rationale**: This preserves Constitution V and the existing decisions in specs 009 and 010; it does not infer that the requested layer is usable merely because a control is visible.

**Alternatives considered**:

- Treat OpenAIP or streets as an automatic WAC fallback: rejected by the constitution and feature 009.
- Enable WAC without the exact current edition, georeferencing, route coverage, authorization, and reproducible delivery evidence: rejected by feature 009.
