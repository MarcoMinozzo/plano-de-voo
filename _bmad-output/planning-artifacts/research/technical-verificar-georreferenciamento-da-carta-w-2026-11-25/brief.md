# Research brief

**Decision:** Determine whether the AISWEB WAC PDF can be used as a locally
georeferenced map layer with radar overlay, without relying on GeoAISWEB WMS.

**Approved scope:** Verify official AISWEB/DECEA distribution formats and
geospatial metadata; check authoritative GDAL and Leaflet documentation for
local raster/tile workflows and their prerequisites.

**Questions**

1. Does AISWEB officially distribute the WAC chart as a GeoPDF or GeoTIFF, or
   only expose a PDF URL?
2. What evidence in the actual chart file is required to establish reliable
   georeferencing?
3. If the file is georeferenced, what is the simplest supported way to serve it
   locally as a Leaflet layer while keeping radar independent?
4. What cannot be concluded without access to the exact WAC PDF?

**Method:** Focused, straightforward technical research using current primary
sources where available. No credentials, authenticated downloads, or attempts
to bypass access challenges.

**Known limitation:** The project workspace does not contain the WAC PDF itself.
Research may identify the official format and viable conversion path, but the
specific file's metadata remains unverified unless an accessible sample is
found.
