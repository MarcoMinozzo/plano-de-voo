# Digest — compatibilidade do tiling, rodada 2

Accessed: 2026-11-25

## Claims

- **Claim:** O GDAL documenta `gdal2tiles` com perfil Mercator e opção `--xyz`, compatível com a numeração XYZ usada por mapas OSM/WMTS; o utilitário pode gerar um diretório de tiles para publicação em servidor web.
  - **Source:** https://gdal.org/en/stable/programs/gdal2tiles.html
  - **Publisher:** GDAL project
  - **Publication date:** not stated
  - **Confidence:** high (direct official documentation fetch)
  - **Class:** implementation capability

- **Claim:** O comando moderno `gdal raster tile` é descrito na documentação como o substituto atual a partir do GDAL 3.13; ele não deve ser assumido disponível no GDAL 3.4.1 instalado nesta máquina.
  - **Source:** https://gdal.org/en/stable/programs/gdal2tiles.html and https://gdal.org/en/stable/programs/gdal_raster_tile.html
  - **Publisher:** GDAL project
  - **Publication date:** not stated; documentation accessed 2026-11-25
  - **Confidence:** high
  - **Class:** version/compatibility

- **Claim:** O executável local `gdal2tiles.py` existe, mas sua invocação carregou uma extensão `gdal_array` incompatível com NumPy 2.2.6 (`_ARRAY_API not found`); portanto, a preparação de tiles não está validada neste ambiente e exige corrigir/alinhação de dependências ou uma ferramenta compatível.
  - **Source:** local command output from `/usr/bin/gdal2tiles.py --help`, accessed 2026-11-25; `gdalinfo --version` reports GDAL 3.4.1
  - **Publisher:** local environment
  - **Publication date:** local package versions as accessed 2026-11-25
  - **Confidence:** high for this environment; not a limitation of GDAL's format support
  - **Class:** local tooling/compatibility

## Limits

- `--help` was queried, not a complete tile-generation run; do not claim a working pipeline.
- The fetched Leaflet API reference redirects to a 2.0 beta page. Reuse the project's pinned 1.9 API behavior or fetch its versioned documentation before relying on version-specific details.
