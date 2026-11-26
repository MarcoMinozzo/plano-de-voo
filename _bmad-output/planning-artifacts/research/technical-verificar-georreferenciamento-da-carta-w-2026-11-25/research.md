---
title: 'technical research: georreferenciamento da carta WAC do AISWEB'
type: 'technical'
topic: 'Verificar georreferenciamento da carta WAC do AISWEB para sobreposição local no mapa'
decision: 'Determinar se o PDF WAC do AISWEB pode ser usado como camada local georreferenciada com radar sobreposto, sem depender do WMS GeoAISWEB'
source: 'native-run'
status: 'complete'
preset: 'standard'
validation: 'normal'
verified_claims: 5
unverified_claims: 1
created: '2026-11-25'
updated: '2026-11-25'
---

# Pesquisa técnica: georreferenciamento da carta WAC do AISWEB

**Decisão que esta pesquisa informa:** determinar se a carta WAC AISWEB em PDF
pode sustentar uma camada local georreferenciada com radar sobreposto, sem o
WMS GeoAISWEB.

## Resumo executivo

**O caminho de carta local é tecnicamente viável para um GeoPDF WAC, mas ainda
não está pronto para substituir o WMS nesta feature.** Baixei uma amostra pública
oficial `WAC 3262 GEOPDF.pdf` e o GDAL 3.4.1 extraiu sistema de coordenadas,
geotransformação afim e extensão WGS84. Isso confirma que uma carta WAC
GeoPDF pode ser georreferenciada sem estimar limites manualmente [2].

Há duas ressalvas decisivas: a amostra é de 2020 e não é a carta atual da rota;
e o `gdal2tiles.py` instalado não concluiu uma geração de tiles por
incompatibilidade entre a extensão `gdal_array` e NumPy 2.2.6 [2][8]. Além
disso, as páginas oficiais consultadas não esclareceram autorização para
redistribuir tiles derivados [7]. Portanto, não usar a amostra como carta do
plano nem publicar tiles até validar o arquivo atual e os termos de uso.

**Recomendação:** manter a integração AISWEB existente e avançar a alternativa
local como candidata: obter, pelo fluxo normal da aplicação, o PDF atual
escolhido para uma rota; confirmar edição, georreferenciamento e cobertura com
GDAL; confirmar autorização de cache/derivação com DECEA; e só então gerar
tiles XYZ num ambiente GDAL/Python compatível e consumi-los como camada do mapa.
O GeoAISWEB continua uma alternativa oficial se liberar o WMS. Não houve
alteração de código nesta pesquisa.

## Evidências e integração

### Formatos e ciclo da carta

O resultado indexado do GeoAISWEB informa downloads de cartas em GeoTIFF e
GeoPDF, incluindo a série visual WAC, mas o acesso direto à página retornou
HTTP 403 nesta pesquisa; essa afirmação fica como pista oficial, não como
confirmação direta [1]. Separadamente, uma URL pública do AISWEB identificada
como `WAC 3262 GEOPDF.pdf` respondeu HTTP 200 e entregou um PDF de 6.071.365
bytes [2].

O eAIP GEN 3.2 atribui ao DECEA responsabilidade pela elaboração/distribuição
das cartas e ao ICA a publicação no AISWEB, inclui WAC na lista de séries e
descreve atualização por emendas AIP [6]. A listagem AISWEB apresenta datas de
efetivação e classificação de uso, mas isso não equivale a licença para
redistribuição de derivados [7].

### Georreferenciamento confirmado na amostra

Com `gdalinfo -json` no PDF público WAC 3262, o driver PDF identificou
geotransform, sistema de coordenadas e extensão WGS84. A extensão calculada
para essa amostra cobre aproximadamente 43,67°W–51,74°W e
19,68°S–24,92°S [2]. O próprio GDAL documenta leitura de PDFs geoespaciais,
extração de georreferenciamento e rasterização; também reconhece PDFs comuns,
por isso a extensão `.pdf` sozinha não garante coordenadas [3].

O arquivo testado tem data de criação 2020-02-12 e cabeçalho HTTP
`Last-Modified` de 2020-05-25. Ele serve exclusivamente para provar que o
formato e o driver funcionam com uma carta WAC; não deve ser apresentado como
carta vigente nem presumido como o arquivo retornado para qualquer rota [2].

### Conversão para mapa e condição do ambiente

O GDAL documenta `gdal2tiles` para gerar pirâmides de tiles em perfil Mercator,
com opção XYZ usada por esquemas de tiles de mapas web [4]. A documentação
Leaflet descreve `ImageOverlay` como uma única imagem posicionada por limites
geográficos; para uma carta que precisa acompanhar vários níveis de zoom, uma
pirâmide de tiles é a abordagem mais apropriada [5].

O `gdalinfo` local (GDAL 3.4.1) conseguiu ler a amostra. Já a execução de
`gdal2tiles.py --xyz -z 3-4` mostrou erro de ABI entre `gdal_array` e NumPy
2.2.6 e ficou ativa por mais de dois minutos; foi encerrada sem validar um
tileset [8]. A documentação mais recente descreve `gdal raster tile` a partir
do GDAL 3.13, recurso que não se deve presumir na instalação atual [4].
Assim, a geração deve ocorrer depois de alinhar GDAL e bindings Python ou em
uma etapa de build com ambiente compatível; não durante o cálculo do plano.

## Contrapontos e limites

- **Amostra de GeoPDF:** prova viabilidade do formato, não atualidade nem
  georreferenciamento do PDF específico escolhido para a rota.
- **Acesso ao GeoAISWEB:** o 403 observado impede confirmar agora a camada WAC
  do WMS; não se tentou contornar desafio ou automatizar navegador [1].
- **Direitos de uso:** não encontrei autorização explícita para armazenar,
  rasterizar e servir tiles derivados. A falta de um aviso encontrado não
  significa permissão nem proibição [7].
- **Tiling local:** documentação dá suporte à conversão, mas o ambiente local
  não concluiu uma geração de tiles [4][8].

## Recomendações para os artefatos de implementação

1. Manter a URL/documento AISWEB atual como fonte da carta enquanto a camada
   local não estiver validada.
2. Como próximo gate técnico, obter o PDF atual selecionado pelo AISWEB para
   uma rota de teste por meio do fluxo autorizado já utilizado pelo usuário.
   Não copiar credenciais para código, logs ou relatório.
3. Executar `gdalinfo` no arquivo exato e registrar edição, CRS, transform,
   extensão e cobertura de todos os pontos da rota. Se faltar georreferência
   ou cobertura, não alinhar por aproximação.
4. Confirmar com DECEA/AISWEB os termos para cache e publicação de tiles
   derivados.
5. Se o gate for aprovado, gerar tiles XYZ fora do cálculo do plano num
   ambiente GDAL/Python compatível; servir a carta como camada de base e manter
   o radar independente. Testar alinhamento usando pontos publicados e estados
   indisponíveis.

## Perguntas em aberto

- Qual é a URL/arquivo e a emenda da carta WAC exata que o AISWEB retorna para
  a rota escolhida?
- O arquivo atual contém georreferenciamento legível por GDAL e cobre toda a
  rota?
- Quais condições oficiais autorizam cache, conversão e distribuição de tiles
  na aplicação?
- Qual ambiente de build/deploy executará GDAL com bindings compatíveis, e
  onde os tiles versionados pela emenda serão armazenados?

## Fontes

| Ref. | Evidência | Publicador | Data de publicação | Acesso | Confiança |
|---|---|---|---|---|---|
| [1] | [GeoAISWEB — visualizador e formatos de carta](https://geoaisweb.decea.mil.br/) | DECEA / GeoAISWEB | Não declarada | 2026-11-25 | Baixa: resultado oficial indexado; acesso direto retornou 403 |
| [2] | [AISWEB — WAC 3262 GeoPDF](https://aisweb.decea.mil.br/cartas/visuais/wac/WAC%203262%20GEOPDF.pdf) | DECEA / ICA | PDF criado em 2020-02-12; HTTP Last-Modified 2020-05-25 | 2026-11-25 | Alta para este arquivo e seus metadados; não comprova vigência |
| [3] | [GDAL — PDF geoespacial](https://gdal.org/en/stable/drivers/raster/pdf.html) | Projeto GDAL | Não declarada | 2026-11-25 | Alta |
| [4] | [GDAL — gdal2tiles](https://gdal.org/en/stable/programs/gdal2tiles.html) e [gdal raster tile](https://gdal.org/en/stable/programs/gdal_raster_tile.html) | Projeto GDAL | Não declarada | 2026-11-25 | Alta |
| [5] | [Leaflet — overlays](https://leafletjs.com/examples/overlays/) | Projeto Leaflet | Não declarada | 2026-11-25 | Alta para o comportamento documentado de imagem com limites |
| [6] | [eAIP GEN 3.2 — Cartas Aeronáuticas](https://aisweb.decea.mil.br/eaip/A%2019-2026_2026_10_01/eAIP/GEN%203.2-pt-BR.html) | DECEA / AISWEB eAIP | Em vigor em 2026-10-01 | 2026-11-25 | Alta |
| [7] | [AISWEB — cartas aeronáuticas](https://aisweb.decea.mil.br/index.cfm?i=cartas&lingua=pt-br) | DECEA / AISWEB | Listagem observada com efetivação em 2026-10-29 | 2026-11-25 | Média para classificação/data; direitos de derivados não esclarecidos |
| [8] | Inspeção local com `gdalinfo --version`, `gdalinfo -json` e tentativa `gdal2tiles.py --xyz -z 3-4` no PDF [2] | Ambiente de execução local | 2026-11-25 | 2026-11-25 | Alta para este ambiente; não é fonte pública |

## Mapa de atualização

Calculado em 2026-11-25 por `recon_kit.py staleness`, com janelas do pack
técnico (compatibilidade: 1 mês; padrões: 24 meses; landscape: 12 meses):

| Evidência | Rechecar até | Estado |
|---|---|---|
| Amostra WAC 3262 criada em 2020-02-12 | 2022-02-12 | Vencida; serve apenas para provar metadados GeoPDF |
| eAIP GEN 3.2, em vigor em 2026-10-01 | 2027-10-01 | Vigente para esta consulta |
| Emenda da listagem AISWEB, 2026-10-29 | 2027-10-29 | Vigente para esta consulta |
| Ambiente local GDAL/NumPy, verificado em 2026-11-25 | 2026-12-25 | Revalidar antes de preparar tiles |

A ferramenta não aceita data de publicação desconhecida. GeoAISWEB, GDAL e
Leaflet não publicaram uma data de atualização identificável nesta consulta;
revalidar essas documentações antes da implementação. A data mais próxima
calculada, 2022-02-12, já passou e refere-se somente à amostra antiga; a próxima
data futura é 2026-12-25 para o ambiente local.
