---
id: SPEC-mapa-interativo-carta-radar
companions:
  - mapa-e-meteorologia.md
  - ../../planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/DESIGN.md
  - ../../planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/EXPERIENCE.md
sources:
  - ../implementation-artifacts/spec-mapa-interativo-carta-radar.md
---

# Mapa técnico com carta, ruas e radar

## Why

Pilotos precisam ler rota, meteorologia e camadas cartográficas sem ruído e sem confundir mapa de ruas com carta visual. Hoje a ficha usa ruas como base fixa, liga o radar automaticamente e apresenta METAR/TAF em texto corrido.

## Capabilities

- **CAP-1**
  - **intent:** O piloto escolhe ruas ou carta visual e controla separadamente a sobreposição de radar.
  - **success:** O radar inicia desligado; em cada base disponível, o piloto consegue ligá-lo e removê-lo sem trocar a base ou perder a rota.
- **CAP-2**
  - **intent:** O piloto consulta METAR/TAF em blocos técnicos concisos por aeródromo e tipo.
  - **success:** Os campos fornecidos, fonte e horário disponíveis são identificáveis, sem valores inferidos ou repetição desnecessária.

## Constraints

- A carta deve usar a fonte oficial GeoAISWEB/GeoServer WMS escolhida pelo usuário; confirmar serviço e identificador WAC antes de implementá-la.
- Se uma camada não estiver disponível, informar indisponibilidade sem fallback silencioso, sem tratar ruas como carta e sem desenhar radar sem georreferenciamento válido.
- A interface desenha a rota calculada pelo servidor; não recalcula navegação nem altera o plano.
- Preservar dados e metadados fornecidos pelas fontes, acessibilidade por toque e teclado e interface em português.
- O radar inicia desligado e só aparece após ação explícita do piloto.

## Non-goals

- Alterar cálculos, dados de rota, autorização de voo ou política operacional.
- Interpretar METAR/TAF, inventar dados ou apresentar a interface como avaliação meteorológica operacional.
- Introduzir outra biblioteca visual.

## Success signal

O piloto alterna entre ruas e carta visual, liga e desliga o radar sobre qualquer base disponível e continua vendo a rota calculada. Dados meteorológicos ficam organizados e indisponibilidades são explícitas; nenhuma camada substitui silenciosamente outra.

## Assumptions

- O serviço WMS e a camada WAC aplicável podem ser confirmados; o endpoint respondeu HTTP 403 neste ambiente e o identificador da camada ainda não foi verificado.
