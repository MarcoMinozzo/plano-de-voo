# Digest — inspeção do GeoPDF público, rodada 1

Accessed: 2026-11-25

## Claims

- **Claim:** O GeoPDF oficial AISWEB `WAC 3262 GEOPDF.pdf` é legível pelo GDAL 3.4.1 local e expõe `geoTransform`, sistema de coordenadas e `wgs84Extent`; portanto, pelo menos esse produto WAC pode ser rasterizado preservando referência espacial, sem estimar bounds manualmente.
  - **Source:** https://aisweb.decea.mil.br/cartas/visuais/wac/WAC%203262%20GEOPDF.pdf
  - **Publisher:** DECEA / AISWEB; inspeção técnica local com GDAL
  - **Publication date:** PDF metadata creation date 2020-02-12; HTTP Last-Modified 2020-05-25
  - **Confidence:** high for this specific sample's embedded georeferencing; not evidence that it is the current chart selected for the route
  - **Class:** geospatial metadata / implementation feasibility

- **Claim:** GDAL inspection yielded a geographic extent for the sample PDF (approximately 43.67°W–51.74°W, 19.68°S–24.92°S), confirming that the returned metadata is spatial and can be evaluated for route coverage.
  - **Source:** same official PDF URL; GDAL 3.4.1 `gdalinfo -json` executed 2026-11-25
  - **Publisher:** DECEA / AISWEB; GDAL project
  - **Publication date:** PDF metadata creation date 2020-02-12; accessed 2026-11-25
  - **Confidence:** high for the sample output
  - **Class:** geospatial metadata / implementation feasibility

## Limits

- This chart file's 2020 metadata makes it a format-test sample only; it must not be used as the current chart for a live route.
- The exact URL selected by the application's authenticated AISWEB API was not accessed or inspected.
- The result proves a local GeoPDF path is technically viable for a GeoPDF WAC, not that every WAC response has the same metadata or that the sample covers the user's route.
