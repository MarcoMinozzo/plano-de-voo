# Interface Contract: Calculated plan screen

## Leg fichas

- The fixed flight summary remains above the leg navigation.
- Each stored leg has a visible label formed from its departure and arrival identifiers.
- Selecting a leg makes exactly its panel active and announces that state accessibly.
- The panel order is: leg measurements, departure METAR, arrival METAR, map, calculated sequence.
- Without JavaScript, all leg panels remain readable and their navigation links continue to reach them.
- The screen has no checklist mark/unmark controls; the PDF retains the suggested checklist.

## Active-leg map

- Only the active leg's departure and arrival points and connecting line are shown.
- Streets is the initial base. A WAC control reports unavailable until feature 009's gates pass. OpenAIP is separate, non-official, attributed, and selectable only when configured and available.
- Radar starts off and can be toggled without changing the base or active leg.
- Missing coordinates or a failed layer are reported explicitly, without using another layer as an unlabeled substitute.
- Tab changes update the active leg display without route recalculation or external weather requests.
- The saved weather snapshot includes each distinct route aerodrome; a leg reads the reports for its own departure and arrival, not the overall plan endpoints.

## Weather

- METAR and TAF are grouped separately for the active leg's departure and arrival.
- For METAR, show the untouched original report, source, report time when supplied, and Portuguese labels/units for non-null structured fields returned by the source.
- Do not infer data from the raw report. Unsupported coded groups remain visible in the original and are not given an invented translation.
- TAF remains original and is not decoded by this feature.
- Missing report or field is represented as unavailable.
