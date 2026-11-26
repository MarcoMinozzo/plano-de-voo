# Digest — geração e consumo de tiles, rodada 2

Accessed: 2026-11-25

## Claims

- **Claim:** O utilitário `gdal2tiles` gera conjuntos de tiles e suporta o perfil Mercator compatível com Google Maps; a opção XYZ corresponde ao padrão de tiles OSM/WMTS, distinto do padrão TMS no eixo Y.
  - **Source:** https://gdal.org/en/stable/programs/gdal2tiles.html
  - **Publisher:** GDAL project
  - **Publication date:** not stated
  - **Confidence:** medium (official search result; direct page verification pending)
  - **Class:** implementation capability

- **Claim:** A documentação atual também descreve `gdal raster tile` para gerar tiles em WebMercatorQuad/EPSG:3857; disponibilidade desse comando depende da versão GDAL instalada e não deve ser presumida para o ambiente atual.
  - **Source:** https://gdal.org/en/stable/programs/gdal_raster_tile.html
  - **Publisher:** GDAL project
  - **Publication date:** not stated
  - **Confidence:** medium (official search result; version compatibility pending)
  - **Class:** version/compatibility

## Follow-up

- Verificar a documentação direta e o CLI local para recomendar o comando compatível com o GDAL 3.4.1 instalado.
- Confirmar o contrato Leaflet para consumir tiles XYZ antes de recomendar URL/estrutura de publicação.
