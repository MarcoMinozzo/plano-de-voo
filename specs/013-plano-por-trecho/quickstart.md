# Quickstart: Tela do plano organizada por trecho

## Automated validation

Run focused tests:

```sh
uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py tests/test_casca_visual.py
```

Tests must use simulated AviationWeather.gov responses and must not depend on external services. Confirm one weather snapshot per distinct route aerodrome, METAR structured fields and raw report, active-leg content, route/map scope, unavailable layers, accessibility states, PDF regression, and absence of checklist actions on the screen.

## Manual validation

1. Open a one-leg plan and confirm the summary sits above the selected leg ficha.
2. Open a multi-leg plan and switch between leg tabs. Confirm each panel is identified by its endpoints and only its METARs, measurements, sequence, and map are active.
3. Confirm the map displays only the selected leg's two endpoints and line. Switch legs and confirm the map updates without a route recalculation.
4. Confirm streets is initially selected, radar is off, and radar can be toggled independently.
5. Confirm the WAC control explicitly says unavailable until the source-validation gates in feature 009 have passed. Confirm it is not replaced by streets or OpenAIP.
6. If OpenAIP is configured, confirm its non-official label and attribution; otherwise confirm an explicit unavailable state.
7. With mocked METAR data for every distinct route aerodrome, compare each Portuguese labeled field and unit to the source JSON, confirm report time/source, and confirm the raw report remains unchanged. Confirm null/unsupported values are not interpreted and switching fichas makes no additional request.
8. Confirm TAF remains raw, weather unavailable states are attached to the correct aerodrome, and the screen has no checklist actions while the PDF still includes its suggested checklist.
9. Repeat at 390 px and 1440 px with keyboard and touch/trackpad. Confirm visible focus and accessible selected-tab state.
10. Disable JavaScript and confirm every leg's content remains readable through the navigation links.
