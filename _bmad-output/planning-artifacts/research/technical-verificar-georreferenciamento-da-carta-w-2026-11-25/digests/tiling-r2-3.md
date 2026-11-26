# Digest — tentativa de geração local de tiles, rodada 2

Accessed: 2026-11-25

## Result

- **Claim:** A tentativa de gerar um pequeno conjunto XYZ com `/usr/bin/gdal2tiles.py --xyz -z 3-4` para o GeoPDF WAC 3262 mostrou incompatibilidade ABI entre `gdal_array` compilado para NumPy 1.x e NumPy 2.2.6. O processo permaneceu ativo por mais de dois minutos e foi encerrado; a geração de tiles não foi validada nesta máquina.
  - **Source:** local command output for the public WAC sample, accessed 2026-11-25
  - **Publisher:** local environment
  - **Publication date:** package/runtime state as accessed 2026-11-25
  - **Confidence:** high for this environment; not a limitation of GeoPDF itself
  - **Class:** local tooling/compatibility

## Limits

- The process was stopped to avoid an unbounded local conversion. Its partial output, if any, is not treated as a valid tileset.
- The PDF's geospatial metadata was successfully read separately with `gdalinfo`; only the tiling step is blocked by the local Python/GDAL ABI mismatch.
