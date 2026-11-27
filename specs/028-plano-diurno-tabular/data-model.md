# Data Model: Plano diurno e relatório organizado

## Existing entities

### `PlanoDeVoo`

The existing plan remains the owner of the saved route, user inputs, result,
meteorology, wind, chart, radar, and status. No table or column is added.

`resultado` remains a JSON object and gains a `programacao` member:

```json
{
  "programacao": {
    "estado": "disponivel",
    "fuso": "UTC",
    "trechos": [
      {
        "ordem": 1,
        "estado": "disponivel",
        "etd": "2026-12-01T12:00:00+00:00",
        "eta": "2026-12-01T13:15:00+00:00",
        "origem": {
          "icao": "SXXX",
          "nascer_do_sol": "2026-12-01T09:10:00+00:00",
          "por_do_sol": "2026-12-01T21:40:00+00:00"
        },
        "destino": {
          "icao": "SYYY",
          "nascer_do_sol": "2026-12-01T09:05:00+00:00",
          "por_do_sol": "2026-12-01T21:35:00+00:00"
        },
        "pernoite": null,
        "fonte": "AISWEB sol"
      }
    ]
  }
}
```

The values above describe the shape only; runtime values must come from the
saved route and AISWEB response. An unavailable schedule uses
`estado: "indisponivel"`, a short reason code, and `null` for uncomputed
times. It must not include guessed solar values.

### `Trecho`

The existing ordered `Trecho` rows remain authoritative for origin/destination
ICAO, route order, distance, heading, duration, fuel, wind state, and their
existing sources. `programacao.trechos[]` joins to them by `ordem`; it does not
duplicate or replace route metrics.

### `Aerodromo`

Use the existing ROTAER name, ICAO, coordinates, telephone, email,
`contatos_rotaer_verificados`, ROTAER version/date, and source fields. Contact
details are shown only when verified. A missing contact remains unavailable;
do not derive or synthesize one.

## Derived view data

### `FonteRelatorio`

Transient server-built row for the source dialog and PDF appendix:

| Field | Meaning |
|---|---|
| `campo` | Report value or group described |
| `fonte` | Provider/publication from saved provenance |
| `publicador` | Publisher when available |
| `referencia` | Manual, chart, data product, or endpoint reference |
| `data` | Edition, update, query, or frame timestamp when available |
| `unidade` | Unit associated with the report value, if applicable |
| `aplicabilidade` | Aircraft variant, route, airport, or data coverage |
| `estado` | Available, unavailable, or not supplied by source |

The data is derived from existing `resultado.procedencia`, `Trecho` source
columns, ROTAER metadata, weather, wind, WAC, and the active radar response.
Do not persist a second copy of this table.

### `CamadaMapa`

Transient descriptor for the map. The WAC descriptor is either a validated
georeferenced layer, the complete ordered set of current official PDFs matched
to the route index, or absent. Street tiles remain the implicit base. Radar
metadata identifies the provider actually selected by the server.

## Validation and state rules

- Every available ETD, ETA, sunrise, and sunset is an ISO-8601 string with an
  explicit UTC offset.
- An available leg requires all solar values needed for both airports and
  dates, `ETD >= origin sunrise`, `ETD <= origin sunset`,
  `ETA <= destination sunset`, and `ETA >= ETD`.
- If the requested time is before origin sunrise, the candidate is advanced
  to that sunrise. If a leg cannot fit, its only retry is the next sunrise at
  the origin; a deferred leg records the origin and date as its overnight.
- Missing, malformed, timezone-naive, or incomplete AISWEB solar data marks
  the schedule unavailable. The route calculation can remain visible, but
  must not be described as a valid daylight schedule.
- A legacy plan without `resultado.programacao` is displayed as not
  calculated; do not infer schedule data on read.
- Source rows may explicitly say unavailable when the stored source metadata
  does not contain a publisher, reference, or date. Never fill those fields
  from assumptions.
- WAC PDF and georeferenced WAC are distinct states. A PDF must never satisfy
  the georeferenced-layer state.
