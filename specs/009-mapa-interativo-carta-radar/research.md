# Research — Mapa interativo com carta e radar

## Decisão vigente — 2026-11-25

- **Decisão**: Avaliar a carta WAC GeoPDF oficial obtida pelo AISWEB como possível fonte de uma camada local. A escolha ainda não autoriza conversão, armazenamento ou publicação de tiles.
- **Gates obrigatórios antes de implementar a carta**:
  1. obter e identificar o PDF da edição oficial vigente aplicável à rota;
  2. validar georreferenciamento e cobertura de todos os pontos da rota nesse arquivo exato;
  3. confirmar que os termos oficiais permitem conversão, cache e disponibilização dos derivados;
  4. demonstrar geração reproduzível de tiles em ambiente compatível, sem executar conversão no cálculo do plano.
- **Se algum gate falhar**: a carta permanece indisponível. Não usar a amostra de 2020, não contornar bloqueios de acesso e não trocar para WMS ou outra fonte sem nova decisão do usuário.
- **Racional**: o `GetCapabilities` do GeoAISWEB retorna HTTP 403 com desafio Cloudflare, enquanto a amostra GeoPDF inspecionada demonstra apenas viabilidade técnica do formato, não vigência, cobertura ou autorização.
- **Decisão anterior, substituída**: a proposta de usar o WMS GeoAISWEB, descrita abaixo, foi abandonada após a confirmação do 403 pelo usuário. Ela permanece registrada como histórico, não como arquitetura aprovada.

## Decisões

### Proposta anterior: camada WAC via WMS (não aprovada)

- **Decisão histórica**: Usar o serviço oficial GeoAISWEB/GeoServer WMS escolhido inicialmente pelo usuário.
- **Racional**: A base WMS permite combinar carta, ruas e radar no mesmo quadro. A consulta sob demanda evita atrasar ou bloquear o cálculo do plano. Se o serviço retornar erro, não listar WAC ou a camada não cobrir a rota, a carta permanece explicitamente indisponível; ruas nunca são substituto.
- **Alternativas consideradas**:
  - Manter somente o PDF/GeoPDF selecionado pelo AISWEB: não produz, por si só, a camada cartográfica necessária para sobrepor radar com georreferenciamento confiável.
  - Usar arquivos GeoTIFF locais: exige fornecer, distribuir e manter as cartas; na decisão histórica, o usuário escolheu a fonte WMS oficial.
  - Limitar o radar ao mapa de ruas: não atende ao pedido de sobreposição sobre carta e ruas.

## Evidências

- O [GeoAISWEB oficial](https://geoaisweb.decea.mil.br/) descreve acesso, via GeoServer, a geosserviços de cartas aeronáuticas e informa disponibilização de cartas em GeoTIFF/GeoPDF.
- Resultados indexados do próprio domínio mostram chamadas WMS no padrão `https://geoaisweb.decea.mil.br/geoserver/ICA/wms`, incluindo exemplos `GetMap` para camadas que não são WAC: [exemplo de camada GeoServer](https://geoaisweb.decea.mil.br/geoserver/ICA/wms/kml?layers=ICA%3ACCV_REA_CY_CUIABA).
- A consulta direta de `GetCapabilities` a `https://geoaisweb.decea.mil.br/geoserver/ICA/wms?service=WMS&request=GetCapabilities` retornou HTTP 403 neste ambiente. Portanto, o nome e a cobertura da camada WAC não foram confirmados.
- A [página oficial de cartas do AISWEB](https://aisweb.decea.mil.br/index.cfm?i=cartas&lingua=pt-br) oferece cartas aeronáuticas; a integração atual do projeto usa a API AISWEB para selecionar WAC e obtém URL/fonte, não uma camada WMS.

## Consequências da proposta WMS anterior (histórico)

- A proposta anterior resolvia a camada somente após ação explícita no botão Carta, fora do cálculo de voo.
- A implementação planejada para WMS validaria o plano pelo piloto autenticado e responderia com estado estruturado, sem expor detalhes técnicos.
- Essa proposta foi substituída; suas regras não autorizam implementar endpoint, parser ou camada WMS.
- Uma validação manual de acesso ao serviço WMS deixa de ser requisito deste caminho, salvo nova decisão do usuário.
- O usuário inicialmente confirmou manter GeoAISWEB WMS e liberar o acesso no ambiente; essa proposta foi posteriormente substituída pela avaliação de GeoPDF local.
- No caminho WMS anterior, o usuário repetiu `GetCapabilities` no host Linux de execução e confirmou HTTP 403, com `server: cloudflare` e `cf-mitigated: challenge`. A recomendação histórica era solicitar ao operador um meio oficial de acesso; não contornar o desafio com cookies, impersonação de navegador ou automação.

## Decisões de interação

- Ruas é a base inicial; radar inicia desligado, conforme decisão do usuário.
- Manter rota/zoom; camadas de fundo são mutuamente exclusivas; radar é independente.
- Usar Leaflet já carregado e os dados JSON existentes. Não adicionar dependência nem migração de banco.
- Organizar METAR/TAF usando campos que a fonte já entrega; manter o texto bruto, horário e fonte identificáveis e campos ausentes explícitos.

## Evidência da avaliação GeoPDF local — 2026-11-25

- Uma carta pública oficial `WAC 3262 GEOPDF.pdf`, criada em 2020, foi lida pelo GDAL 3.4.1. `gdalinfo` extraiu sistema de coordenadas, geotransformação afim e extensão WGS84. Isso confirma a viabilidade do formato GeoPDF, não a vigência nem a cobertura do arquivo selecionado para uma rota.
- O GDAL documenta geração de tiles XYZ; a tentativa local não foi concluída devido a incompatibilidade ABI entre `gdal_array` e NumPy 2.2.6. A preparação deve ocorrer em ambiente GDAL/Python compatível e fora do cálculo do plano.
- Não foi localizada autorização explícita para cache, conversão e distribuição de tiles derivados. Confirmar os termos com DECEA/AISWEB antes de publicar tiles.
- **Estado:** candidato local ainda não aprovado. O PDF exato retornado pela API AISWEB para a rota continua sem inspeção; validar arquivo, cobertura e termos de uso antes de qualquer conversão ou publicação.
- Relatório técnico completo: [`pesquisa do GeoPDF e tiles`](../../_bmad-output/planning-artifacts/research/technical-verificar-georreferenciamento-da-carta-w-2026-11-25/research.md).

## Busca de fonte alternativa licenciada — 2026-11-25

- A busca encontrou a [Política de Uso do AISWEB](https://ajuda.decea.mil.br/poltica-de-uso-aisweb), cujo resultado oficial informa restrição de uso do conteúdo, salvo uso regulamentado ou autorizado. A página direta retornou HTTP 403 nesta sessão; não foi possível confirmar os termos completos nem autorização para gerar/servir tiles.
- O GeoAISWEB oferece cartas GeoPDF/GeoTIFF e geosserviços, mas o WMS continua retornando 403 e não é uma fonte alternativa acessível validada.
- O [OpenAIP](https://www.openaip.net/legal) fornece uma camada combinada de tiles PNG XYZ e PBF, consumível por clientes de mapa, incluindo Leaflet. A API oficial exige uma chave criada na conta do provedor, atribuição visível e impõe limites de uso. Os dados são CC BY-NC 4.0 e não são uma carta WAC oficial nem uma representação topográfica equivalente.
- O catálogo de metadados da INDE contém registros de cartas WAC publicadas pelo ICA/DECEA, mas não mostrou licença independente; a consulta direta ao registro retornou HTTP 503. O visualizador GeoAISWEB e sites terceiros que mostram cartas ao vivo continuam usando a mesma fonte AISWEB/DECEA, não autorizando derivados.
- **Resultado:** não foi identificada uma fonte alternativa licenciada que seja uma WAC atual. OpenAIP é tecnicamente uma camada aeronáutica alternativa, mas não substitui nem pode ser rotulada como WAC.
- **Bloqueio de produto:** a constituição atual fixa a carta visual vigente como AISWEB e determina indisponibilidade sem sua chave. OpenAIP só pode ser considerado após alteração explícita dessa regra, atribuição/termos cumpridos e configuração da chave no ambiente; não há chave OpenAIP configurada.
- **Caminho AISWEB:** aguardar autorização oficial para os derivados da WAC e validar arquivo/cobertura, sem publicar tiles antes.
