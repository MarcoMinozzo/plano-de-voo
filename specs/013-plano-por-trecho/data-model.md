# Data Model: Tela do plano organizada por trecho

This feature adds no database entity or schema migration.

## Plan weather snapshot

The existing `PlanoDeVoo.meteorologia` JSON may retain additional optional fields from the existing AviationWeather.gov METAR response:

- Station identifier and report time.
- Original report text (`rawOb`), unchanged.
- Temperature and dew point in Celsius.
- Wind direction in degrees or the source's `VRB` value; wind speed and gust in knots.
- Visibility in the source unit (statute miles).
- Altimeter setting in hPa.
- Present-weather code, vertical visibility, and cloud layers only when returned.
- Source identity.

Absent or null values remain absent/null and render as unavailable. The UI must not infer fields from raw text. The existing `origem` and `destino` weather blocks remain unchanged for PDF compatibility. An additional `aerodromos` object is keyed by ICAO for each distinct aerodrome in the stored route; each leg ficha reads its departure and arrival blocks from this object. If a station has no report, its state remains unavailable.

## Leg map input

The plan's existing ordered legs supply the two endpoint coordinates for each map view. The coordinates are transient presentation inputs derived from the stored aerodrome catalog; they do not alter the route or become new persisted data.
