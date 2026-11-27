# Research: Plano diurno e relatório organizado

## AISWEB solar data

- **Decision**: Continue using the official AISWEB `sol` area, queried by
  aerodrome indicator and date. Parse both sunrise and sunset, preserve the
  returned UTC instants, and treat missing, malformed, or incomplete pairs as
  unavailable.
- **Rationale**: The current integration already requests `area=sol` with
  `icao` and `dt`, but only recognizes sunset. AISWEB's API overview identifies
  `sol` as its sunrise/sunset service and states that responses are XML. The
  current eAIP GEN 2.7 specifies the aerodrome ARP and says results are in UTC.
  The application must not substitute a locally computed solar time when the
  official source fails.
- **Alternatives considered**: Calculate sunrise/sunset from coordinates;
  rejected because the feature requires AISWEB and the constitution prohibits
  inventing official data. Store local time; rejected because the source
  presents UTC and route legs may cross Brazilian time zones.
- **References**:
  - [AISWEB API documentation](https://documenter.getpostman.com/view/7201070/SzKQyg3H)
  - [AISWEB eAIP GEN 2.7, Nascer/Pôr do Sol](https://aisweb.decea.mil.br/eaip/A%2019-2026_2026_10_01/eAIP/GEN%202.7-pt-BR.html)
  - Existing integration: `servidor/rotaer_aisweb.py:258-296`

## AISWEB WAC records and PDF behavior

- **Decision**: Request current visual WAC records through the AISWEB chart
  area using the documented VFR/WAC filters and current cycle. The documented
  response provides a PDF `link`, chart identity/name, locality reference,
  and cycle/publication metadata; it does not document geospatial bounds.
  Therefore, a PDF URL alone is never evidence of route coverage or
  georeferencing. A PDF fallback is offered only after matching every route
  leg to official WAC index entries; show matched sheets in route order when
  more than one is needed. Otherwise hide the control. Never open an arbitrary
  WAC sheet or present it as an overlay.
- **Rationale**: The AISWEB API documents `indiceMapa` as the visual-chart
  index filter and WAC as a VFR chart type. The current eAIP GEN 3.2 includes
  the WAC index. This supports deterministic official sheet selection while
  preserving the distinction between an official PDF and a georeferenced
  raster layer.
- **Alternatives considered**: Select the first returned PDF; rejected because
  it may not cover the route. Infer bounds from PDF dimensions or a URL;
  rejected because neither proves geographic coverage. Keep the WAC control
  visible with an error message; rejected because the approved UX hides
  unavailable controls and avoids redundant body messages.
- **References**:
  - [AISWEB API documentation](https://documenter.getpostman.com/view/7201070/SzKQyg3H)
  - [AISWEB eAIP GEN 3.2, Aeronautical Charts](https://aisweb.decea.mil.br/eaip/A%2019-2026_2026_10_01/eAIP/GEN%203.2-pt-BR.html)
  - Existing selector: `servidor/tempo.py:250-275`

## Radar provider fallback

- **Decision**: Keep REDEMET as the first choice and use the single radar
  resolver to select RainViewer only when REDEMET is unavailable for the
  route. Keep provider choice on the server and return enough metadata for
  the client to display attribution, frame time, and coverage caveat.
- **Rationale**: The project's Constitution v8.0.1 allows this automatic
  fallback only for educational use and requires visible identification and
  attribution. RainViewer's current API terms state personal/educational use,
  best-effort availability, and visible credit with a link.
- **Alternatives considered**: Expose separate buttons; rejected by the
  approved UX. Treat RainViewer as official radar; rejected by source terms
  and the Constitution. Hide source identity; rejected because attribution
  and provenance must remain visible.
- **References**:
  - [RainViewer API documentation and terms](https://www.rainviewer.com/api.md)
  - Existing provider code: `servidor/rainviewer.py`
  - Current page controls: `templates/plano.html:150-167`

## Existing persistence and report patterns

- **Decision**: Store each leg's schedule in the existing
  `PlanoDeVoo.resultado` JSON, keyed by route order. Build the source table
  from existing provenance fields and verified ROTAER contacts; do not add
  database tables or dependencies.
- **Rationale**: `PlanoDeVoo.resultado` already stores JSON calculation
  results, and `Aerodromo` already contains `telefone`, `email`,
  `contatos_rotaer_verificados`, source, and ROTAER version metadata.
  `Trecho` already stores ordered route metrics and source strings. A
  JSON-safe schedule avoids a migration while retaining the exact calculated
  dates on each saved plan.
- **Alternatives considered**: Add individual ETD/ETA/solar columns to
  `trecho`; rejected because the schedule is a cohesive structured result and
  would require a migration. Recompute on page render; rejected because it
  would make saved reports vary with current external data and issue calls
  when the user only opens a plan.
- **References**:
  - `servidor/modelos.py:175-193` (`Aerodromo`)
  - `servidor/modelos.py:203-228` (`PlanoDeVoo`)
  - `servidor/modelos.py:248-273` (`Trecho`)
  - `servidor/planos_consulta.py:70-145` (JSON serialization)
  - `servidor/planos.py:244-350` (plan calculation and persistence)

## Scheduling rules

- **Decision**: Use existing per-leg flight duration. For each leg, choose the
  earliest candidate from the requested departure or preceding ETA, but not
  before origin sunrise. Require ETD to be at or before origin sunset and ETA
  to be at or before destination sunset. If the leg does not fit, retry at the
  next origin sunrise once; record an overnight at that origin. If it still does
  not fit or any needed solar value is unavailable, mark the schedule
  unavailable and do not invent a stop or ground time.
- **Rationale**: This implements the user's next-day/pernoite requirement,
  keeps comparisons in UTC, and bounds retries. The selected route remains
  governed by the existing fuel/weight algorithm; the schedule does not
  silently change the route.
- **Alternatives considered**: Add unprovided ground time; rejected because it
  would invent a value. Retry indefinitely; rejected because external data
  calls could be unbounded and the spec requires an unavailable state rather
  than endless deferral. Add airports to make daylight fit; rejected because
  route selection must remain explicit and based on existing criteria.
- **Reference**: `servidor/rota.py:179-240` currently filters route candidates
  by sunset and must hand off that responsibility to the schedule step.
