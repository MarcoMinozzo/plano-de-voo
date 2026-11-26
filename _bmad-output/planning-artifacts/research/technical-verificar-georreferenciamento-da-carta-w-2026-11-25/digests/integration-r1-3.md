# Digest — acesso público ao PDF, rodada 1

Accessed: 2026-11-25

## Claims

- **Claim:** O endpoint público oficial AISWEB para `WAC 3262 GEOPDF.pdf` respondeu HTTP 200, `Content-Type: application/pdf`, `Content-Length: 6,071,365` e `Last-Modified: 2020-05-25`; a transferência excedeu 20 segundos e foi interrompida após 3,571,276 bytes.
  - **Source:** https://aisweb.decea.mil.br/cartas/visuais/wac/WAC%203262%20GEOPDF.pdf
  - **Publisher:** DECEA / AISWEB
  - **Publication date:** file header reports last modified 2020-05-25
  - **Confidence:** high for response headers; PDF body was incomplete
  - **Class:** endpoint/access

- **Claim:** `gdalinfo` is installed in this environment as GDAL 3.4.1.
  - **Source:** local command `gdalinfo --version`, executed 2026-11-25
  - **Publisher:** local environment
  - **Publication date:** release date reported by command: 2021-12-27
  - **Confidence:** high for this environment only
  - **Class:** local tooling

## Gaps

- The partial transfer was discarded; no PDF content or geospatial metadata was inspected yet.
- This public chart is only an example and may not be the exact WAC URL selected for the user's route.
