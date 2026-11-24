---
name: Plano de voo
description: Casca visual do planejamento de voo visual, com o emblema, o blueprint da pista e fichas por trecho.
status: final
sources:
  - specs/004-enxugar-tela-piloto/spec.md
updated: 2026-11-24
colors:
  navy: '#001030'
  sky: '#0090F0'
  gold: '#F0A000'
  paper: '#F4F7FB'
  glass: '#1C3348'
  ink-on-paper: '#001030'
  muted: '#8AA0B8'
typography:
  title:
    fontFamily: sans-serif
    fontSize: 1.75rem
    fontWeight: '700'
    lineHeight: '1.25'
  body:
    fontFamily: sans-serif
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: '1.45'
  meta:
    fontFamily: sans-serif
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 8px
  md: 16px
  lg: 24px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  gutter: 16px
  margin-mobile: 12px
components:
  page-background:
    image: imports/blueprint-airport-runway.jpg
    scrim: '{colors.navy}'
  emblem:
    image: imports/emblema-plano-de-voo.png
    maxWidth: 168px
  glass-card:
    background: '{colors.glass}'
    text: '{colors.paper}'
    radius: '{rounded.lg}'
    padding: '{spacing.5}'
  text-field:
    background: '{colors.paper}'
    text: '{colors.ink-on-paper}'
    radius: '{rounded.sm}'
  primary-button:
    background: '{colors.gold}'
    text: '{colors.navy}'
    radius: '{rounded.md}'
  menu-bar:
    background: '{colors.navy}'
    text: '{colors.paper}'
    accent: '{colors.gold}'
  leg-tab:
    background: '{colors.navy}'
    text: '{colors.paper}'
    active: '{colors.gold}'
    radius: '{rounded.md}'
  measure-field:
    background: '{colors.paper}'
    text: '{colors.ink-on-paper}'
    label: '{colors.navy}'
    radius: '{rounded.sm}'
  disclaimer:
    text: '{colors.paper}'
---

## Brand & Style

O Plano de voo parece um documento de preparação sobre a planta azul do aeroporto. O emblema traz o avião, a rosa dos ventos e o globo. A tela fica calma: um card de cada vez, fichas com aba, e o aviso de que o resultado apoia o planejamento e não autoriza o voo.

A voz visual é técnica e direta. O azul escuro carrega o texto sobre o vidro. O amarelo marca a ação principal e a aba da frente. O azul claro marca o dado disponível. O branco é o papel onde o número é lido.

As imagens de referência estão em `imports/blueprint-airport-runway.jpg` e `imports/emblema-plano-de-voo.png`. As telas de referência estão em `mockups/key-entrar.html`, `mockups/key-processando.html` e `mockups/key-plano.html`. Os documentos de desenho e de experiência vencem qualquer mock se houver conflito.

## Colors

`{colors.navy}` é o azul escuro do emblema. Serve ao menu, às abas em espera e ao véu sobre o blueprint, para a planta não competir com o texto.

`{colors.sky}` é o azul claro do céu no emblema. Serve a um dado disponível e ao traço do trecho no mapa. Não serve a texto pequeno sobre `{colors.glass}`.

`{colors.gold}` é o amarelo do aro do emblema. Serve ao botão principal e à aba da ficha da frente. O texto sobre esse amarelo é `{colors.navy}`.

`{colors.paper}` é o branco de leitura. Serve aos campos e ao miolo da ficha.

`{colors.glass}` é o azul acinzentado do card. A opacidade do vidro é 82% sobre o blueprint. O valor sólido de referência é `{colors.glass}`.

`{colors.muted}` nomeia fonte, unidade repetida e medida indisponível. Não esconde o aviso de que o resultado não autoriza o voo.

Contraste de leitura: `{colors.paper}` sobre `{colors.navy}` e sobre `{colors.glass}` passa de 12:1. `{colors.navy}` sobre `{colors.gold}` passa de 8:1. `{colors.paper}` sobre `{colors.sky}` não é combinação de texto.

## Typography

A página continua em sans-serif, como a tela já entregue. Os três papéis são `{typography.title}`, `{typography.body}` e `{typography.meta}`. Não entra arquivo de fonte novo.

O título nomeia a tela ou a rota. O corpo carrega o valor e a frase de planejamento. O meta carrega unidade, fonte e a palavra indisponível.

## Layout & Spacing

A tela estreita, abaixo de 720 px, é uma coluna. 720 px é o corte. A margem é `{spacing.margin-mobile}`. O card ocupa a largura útil. O menu quebra em duas linhas de botões, com área de toque de pelo menos 44 px.

A tela larga centra o card de vidro até 40 rem. As fichas continuam uma coluna de leitura. As abas ficam numa faixa horizontal que rola quando não cabem.

A escala é `{spacing.1}` a `{spacing.6}`. O espaço entre blocos da ficha é `{spacing.5}`.

## Elevation & Depth

O blueprint fica no fundo, inteiro, sem repetir em mosaico. Um véu `{colors.navy}` a 35% segura o contraste.

O card de vidro é a única superfície elevada. A ficha da frente senta sobre as outras, com a aba em `{colors.gold}`. Não há sombra colorida nem segunda camada de modal.

## Shapes

O card usa `{rounded.lg}`. O botão e a aba usam `{rounded.md}`. O campo usa `{rounded.sm}`. O emblema permanece circular, como o arquivo.

## Components

**page-background.** A imagem `imports/blueprint-airport-runway.jpg` cobre a viewport. O véu `{colors.navy}` fica por cima. Nenhuma tela troca essa imagem.

**emblem.** O arquivo `imports/emblema-plano-de-voo.png` aparece no login, no cadastro e no menu. Largura máxima 168 px. No menu estreito, a largura máxima cai para 72 px.

**glass-card.** Fundo `{colors.glass}`, texto `{colors.paper}`, raio `{rounded.lg}`, padding `{spacing.5}`. O emblema fica no topo. O aviso de planejamento fica visível sem rolagem extra dentro do card de entrada.

**text-field.** Fundo `{colors.paper}`, texto `{colors.ink-on-paper}`, raio `{rounded.sm}`, rótulo em `{typography.meta}` acima do controle. A caixa de uma linha usa o mesmo papel.

**primary-button.** Fundo `{colors.gold}`, texto `{colors.navy}`, raio `{rounded.md}`. Uma ação principal por card.

**menu-bar.** Fundo `{colors.navy}`, texto `{colors.paper}`, ação corrente com um fio `{colors.gold}` de 2 px. Quatro ações: Novo voo, Voos planejados, Imprimir voo, Sair.

**processing.** Ampulheta em `{colors.gold}` girando sobre o blueprint, com a frase "Em processamento" em `{colors.paper}`. O card de entrada não permanece visível.

**summary-card.** Mesmo vidro do `{components.glass-card}`. Fica acima das fichas e não troca quando a aba troca. Cada linha resume um trecho pelos códigos e pelos números já gravados.

**leg-tab.** Aba com os códigos de saída e chegada. A da frente usa `{colors.gold}` e texto `{colors.navy}`. As outras usam `{colors.navy}` e texto `{colors.paper}`.

**leg-ficha.** Miolo `{colors.paper}`, texto `{colors.ink-on-paper}`, raio `{rounded.lg}`. A ordem visual é dados do trecho, METAR, mapa, sequência calculada.

**measure-field.** Rótulo `{colors.navy}` e valor `{colors.ink-on-paper}` em `{colors.paper}`. Unidade no rótulo quando a grandeza a tem. Indisponível em `{colors.muted}`, sem número no lugar.

**map-panel.** Faixa de botões acima do mapa: Carta de voo visual, Mapa de ruas, Radar de chuva. O botão escolhido usa `{colors.gold}`. O mapa ocupa a largura da ficha e tem controle de zoom.

**sequence-line.** Texto `{typography.body}` depois do mapa, em `{colors.ink-on-paper}`. Só a sequência calculada.

**disclaimer.** Frase em `{colors.paper}` sobre o vidro, ou em `{colors.ink-on-paper}` no miolo da ficha. Permanece visível na entrada e no plano.

## Do's and Don'ts

Faça o fundo ser a planta da pista em todas as telas. Faça o emblema ser o logo. Faça o amarelo indicar a ação ou a ficha da frente. Nomeie unidade e fonte. Escreva indisponível quando o dado não veio. Mantenha a frase de que o resultado não autoriza o voo.

Não troque a planta por cor chapada. Não desenhe outra carta quando a carta de voo visual falta. Não apresente o mapa de ruas como carta. Não invente medida de METAR. Não ensine técnica de decolagem nem de pouso. Não coloque o checklist na tela. Não use uma biblioteca visual nova.
