# Contract: Aircraft Selection and Report

## New-Plan Form

- Keep factual aircraft and synthetic profiles in separate categories.
- Offer exactly the twenty established synthetic profiles when present.
- The option text is only the correct associated model name; do not include `DEMO`, `Proxy`, or `sintético` in the option name.
- Keep one disclosure at the end of the input card, after the form controls. State that calculations and profile data are educational, synthetic and unvalidated, do not represent the associated model, do not replace the manual, training, or current regulations, are unsuitable for real-flight planning, and do not authorize flight.
- Preserve the existing generic no-real-flight/no-authorization notice for factual aircraft.

## Plan Result and PDF

- Continue displaying the correct model name and identifying each synthetic field and its unit.
- The PDF retains the existing pilot guidance and appends the synthetic-profile disclaimer after it, as the final report content.
- The final disclosure states that calculations and profile values are educational, synthetic and unvalidated, do not represent the associated model, do not replace the manual, training, or current regulations, are unsuitable for real-flight planning, and do not authorize flight.
- Ordinary factual-aircraft reports retain their current behavior.

## Catalogue Response

- Keep the existing `/aeronaves` response shape and separate `modelos` and `perfis_sinteticos` collections.
- Synthetic profile `nome` values use the correct model names; the synthetic `rotulo` remains an explicit safety indicator and is not concatenated into the form option text.
