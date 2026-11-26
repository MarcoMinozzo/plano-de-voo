# Digest — integração e formatos, rodada 1

Accessed: 2026-11-25

## Claims

- **Claim:** O visualizador oficial GeoAISWEB informa que disponibiliza cartas aeronáuticas nos formatos GeoTIFF e GeoPDF e lista cartas visuais WAC.
  - **Source:** https://geoaisweb.decea.mil.br/
  - **Publisher:** DECEA / GeoAISWEB
  - **Publication date:** not stated
  - **Confidence:** medium (official search result; direct page verification pending)
  - **Class:** official product format/distribution

- **Claim:** O domínio oficial AISWEB indexa uma carta WAC com URL cujo nome contém `GEOPDF`, evidência de que pelo menos uma carta WAC é publicada como PDF geoespacial.
  - **Source:** https://aisweb.decea.mil.br/cartas/visuais/wac/WAC%203262%20GEOPDF.pdf
  - **Publisher:** DECEA / AISWEB
  - **Publication date:** not stated in search result
  - **Confidence:** medium (official URL and indexed chart content; file metadata not yet inspected)
  - **Class:** official product format/distribution

- **Claim:** O driver PDF do GDAL pode ler PDFs geoespaciais, extrair georreferenciamento e rasterizar o conteúdo; PDFs sem georreferenciamento também são reconhecidos, portanto a presença de um PDF não prova que ele tenha coordenadas.
  - **Source:** https://gdal.org/en/stable/drivers/raster/pdf.html
  - **Publisher:** GDAL project
  - **Publication date:** not stated
  - **Confidence:** high (official driver documentation)
  - **Class:** implementation capability

- **Claim:** O `ImageOverlay` do Leaflet posiciona uma única imagem usando limites geográficos informados; portanto a aplicação precisa de bounds confiáveis, e essa API não extrai georreferenciamento do PDF.
  - **Source:** https://leafletjs.com/examples/overlays/
  - **Publisher:** Leaflet project
  - **Publication date:** not stated
  - **Confidence:** high (official Leaflet documentation)
  - **Class:** integration requirement

## Leads and gaps

- Buscar verificação direta da página oficial GeoAISWEB e do PDF WAC identificado.
- O PDF específico retornado pela API AISWEB no projeto não está disponível nesta pesquisa; não concluir que ele é GeoPDF só porque existe uma carta WAC pública com `GEOPDF` no nome.
- Confirmar quais ferramentas e formatos a conversão local exigiria e como servir imagens em diferentes níveis de zoom.
