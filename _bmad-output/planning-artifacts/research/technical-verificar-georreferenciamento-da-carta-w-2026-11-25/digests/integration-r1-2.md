# Digest — verificação direta, rodada 1

Accessed: 2026-11-25

## Claims

- **Claim:** O resultado oficial do GeoAISWEB declara disponibilizar cartas aeronáuticas em GeoTIFF e GeoPDF, incluindo cartas visuais WAC.
  - **Source:** https://geoaisweb.decea.mil.br/
  - **Publisher:** DECEA / GeoAISWEB
  - **Publication date:** not stated
  - **Confidence:** medium (official search index result; direct page fetch returned HTTP 403)
  - **Class:** official product format/distribution

- **Claim:** O AISWEB indexa uma carta WAC com nome de arquivo `WAC 3262 GEOPDF.pdf`; isso confirma a existência de ao menos um WAC publicado como GeoPDF, mas não confirma que seja o PDF atualmente retornado para qualquer rota pelo projeto.
  - **Source:** https://aisweb.decea.mil.br/cartas/visuais/wac/WAC%203262%20GEOPDF.pdf
  - **Publisher:** DECEA / AISWEB
  - **Publication date:** not stated
  - **Confidence:** medium (official indexed URL; direct fetch timed out, so PDF bytes and embedded metadata were not inspected)
  - **Class:** official product format/distribution

- **Claim:** GDAL's PDF raster driver can extract georeferencing and rasterize a geospatial PDF; it also recognizes non-geospatial PDFs, so the file itself must be inspected before choosing this workflow.
  - **Source:** https://gdal.org/en/stable/drivers/raster/pdf.html
  - **Publisher:** GDAL project
  - **Publication date:** not stated; documentation is current as accessed 2026-11-25
  - **Confidence:** high (direct official documentation fetch)
  - **Class:** implementation capability

- **Claim:** Leaflet `ImageOverlay` accepts one image and geographic bounds; overlay alignment therefore requires correct bounds, while a large/zoomable raster would need a tile-serving approach rather than assuming one image fits every zoom.
  - **Source:** https://leafletjs.com/examples/overlays/
  - **Publisher:** Leaflet project
  - **Publication date:** not stated; documentation fetched 2026-11-25
  - **Confidence:** high (direct official documentation fetch)
  - **Class:** integration requirement

## Acquisition results and gaps

- Direct fetch of the GeoAISWEB homepage returned HTTP 403; no challenge was bypassed.
- Direct fetch of the indexed WAC GeoPDF timed out; no credentials or alternate access methods were used.
- The exact PDF returned by the application's AISWEB API remains unverified. The public evidence supports that official WAC GeoPDF/GeoTIFF products exist, not that every API result is georeferenced or that the project's selected PDF is one of them.
- Follow-up needed: obtain a specific chart file through an authorized user workflow and inspect it with GDAL (`gdalinfo`) for CRS, geotransform/GCPs, neatline, and rasterization support.
