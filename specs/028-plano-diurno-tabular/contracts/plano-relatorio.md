# Contract: Plano, mapa e relatório

## Authenticated plan detail

Keep the existing owner-filtered `GET /planos/<plano_id>` HTML and JSON
contract. Extend its view data/JSON with:

- The complete ordered route, including the full names of each leg's origin
  and destination and verified route-endpoint contacts when present.
- The saved `resultado.programacao` joined to legs by `ordem`.
- A server-built `fontes_relatorio` list for the information icon and PDF
  appendix.
- WAC descriptors only when every required current official chart is proven
  relevant to the route. A PDF descriptor is explicitly `tipo: "pdf"`; a
  validated map layer is explicitly `tipo: "georreferenciada"`.

The existing 404 behavior for a plan not owned by the session user remains
unchanged. Do not expose AISWEB or REDEMET credentials in the response.

## Radar resolver

Add one authenticated route, `GET /planos/<plano_id>/camadas/radar`, using the
same plan ownership check as existing map-layer routes. An optional
`exclude=REDEMET` or `exclude=RainViewer` is accepted only for the single
automatic retry after a tile-load failure; reject other values. The client
must not retry more than once for the same activation.

Available response:

```json
{
  "estado": "disponivel",
  "provedor": "REDEMET",
  "fonte": "REDEMET MaxCappi",
  "hora_frame": "2026-12-01T12:00:00+00:00",
  "radar_url": "...",
  "atribuicao": null,
  "aviso_cobertura": null
}
```

For RainViewer, `provedor` and `fonte` identify RainViewer, `atribuicao`
contains its visible linked credit, and `aviso_cobertura` states the limitation.
The response must include the provider's actual frame timestamp. Unavailable
responses use `estado: "indisponivel"` and do not return a tile URL.

The server selects REDEMET first and RainViewer only as the permitted
educational fallback. The client only toggles the layer and presents returned
metadata. A tile-load failure may trigger one resolver retry excluding the
failed provider; it must not create another visible provider control.

## WAC control

- Render at most one control labelled “Carta WAC”; do not render OpenAIP,
  Google Maps, or a separate street-map control.
- When the descriptor is georeferenced, toggle that validated layer.
- When descriptors are PDFs, open the single matched document or show the
  complete route-ordered set of links in one accessible WAC dialog; do not add
  them as map layers.
- When neither descriptor is valid, omit the control and keep streets as the
  implicit base. Do not print a redundant unavailability message.
- Never render an AISWEB PDF link as evidence that the route is covered, and
  do not show a partial set when the route needs multiple WAC sheets.

## Report and source dialog

- The first report card summarizes the full route in order.
- Tables group flight, aircraft, route, airport, solar, and weather data.
- Every leg shows full airport names, ETD/ETA, and applicable sunrise/sunset
  values or an explicit unavailable state.
- The sources icon sits next to the print action at the top. It opens an
  accessible native dialog containing a field-to-source table. Close by
  button and Escape; keep keyboard focus within the open dialog.
- The PDF includes sources in a separate appendix/table, not beside every
  value in the main report.
- Weight and limit violations are red and have explanatory text, so status
  does not depend on color alone.
- The main report keeps the existing educational notice. It omits “Como ler
  este plano” and does not add a print action at the bottom.
- At desktop widths the report container is approximately 80% of the useful
  viewport; at 390 px it fits without global horizontal scrolling.

## Compatibility

Plans saved before this feature have no schedule member. Keep them readable
and return/display schedule state `indisponivel` or `nao_calculada`; do not
make external solar requests just because a plan was opened. Existing update
flow recalculates and persists the new schedule.
