---
title: 'Mapa quadrado com satélite REDEMET e opção WAC visível'
type: 'feature'
created: '2026-11-27'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '6de1edde15ea9090ee84cec2696a591d96fdd04e'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/009-mapa-interativo-carta-radar/spec.md'
  - '{project-root}/specs/009-mapa-interativo-carta-radar/plan.md'
  - '{project-root}/documentacao/piloto.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O mapa da ficha exibe ruas como base e a carta AISWEB apenas como link; o piloto não consegue consultar a WAC georreferenciada junto da rota.

**Approach:** Implementar a carta WAC oficial vigente como base selecionável no Leaflet, com ruas como alternativa, mantendo a rota e permitindo controlar o radar como sobreposição independente. A carta só aparece depois de validar o arquivo exato, sua cobertura, a autorização de uso e a geração de tiles.

## Boundaries & Constraints

**Always:** Preservar a rota e o cálculo no servidor. Usar edição WAC oficial vigente, georreferenciamento e cobertura verificados para todos os pontos. Identificar AISWEB/DECEA e a edição da carta. Exibir indisponibilidade sem fallback enganoso. Gerar tiles fora do cálculo e da abertura do plano. Só habilitar a camada após o usuário fornecer uma fonte atual e autorização/licença verificável; até lá, não gerar nem servir tiles. Manter a interface em português, responsiva e acessível.

**Never:** Usar a amostra WAC de 2020 como edição atual; estimar coordenadas; contornar o desafio Cloudflare; converter, armazenar ou servir derivados sem autorização oficial; recalcular a rota no navegador; identificar ruas como carta.

## I/O & Edge-Case Matrix

| Cenário | Estado | Resultado esperado | Erro |
|---|---|---|---|
| Carta válida | Tilepack autorizado, edição atual e cobertura completa | Selecionar carta; manter rota, zoom e radar alinhados | Nenhuma |
| Fonte pendente | PDF, permissão ou tiles não validados | Carta indisponível; ruas continuam uma base distinta | Mensagem explícita |
| Falha de tile | Erro ao carregar um tile da carta | Remover camada defeituosa e informar indisponibilidade | Não trocar base silenciosamente |
| Radar | Imagem e limites válidos | Piloto liga/desliga o radar sem trocar a base | Sem limites válidos, não exibir overlay |
| Sem rota | Menos de dois pontos | Não mostrar mapa sem função | Não inventar pontos |

</frozen-after-approval>

## User Request Addendum

- Em telas desktop, o quadro do mapa deve ser quadrado; em telas pequenas, preservar a altura atual.
- Adicionar uma sobreposição opcional de imagem de satélite REDEMET, separada do radar e ativada sob demanda. Usar o frame mais recente válido do produto `realcada`, seus limites geográficos e horário retornados pela API; não expor a chave REDEMET no navegador.
- Manter o controle “Carta WAC” visível. Quando houver documentos AISWEB válidos, ele abre os links existentes; sem documentos, fica desabilitado e informa que a carta está indisponível. Não apresentar PDF como camada raster nem contornar os gates de autorização, edição, georreferenciamento e cobertura já definidos.

## Code Map

- `servidor/tempo.py:radar` — padrão existente para consultar REDEMET com `REDEMET_API_KEY`; `carta` consulta AISWEB e retorna documentos, sem converter PDFs.
- `app.py:camada_radar` — padrão de endpoint autenticado que verifica o piloto dono antes de resolver uma camada.
- `templates/plano.html:#mapa` — mapa Leaflet e controles; `wac-toggle` só é renderizado quando há PDF, `radar-toggle` é independente, e o mapa tem altura fixa de 20rem.
- `tests/test_tempo.py`, `tests/test_tela_piloto.py` — mocks da API e testes de rota autenticada, controles, WAC disponível e estado do radar; estender com estados de satélite e WAC indisponível.
- `static/css/input.css` e `package.json` — fonte e comando de geração do CSS Tailwind; classes novas precisam constar no template e no CSS gerado.
- `documentacao/piloto.md` — instruções atuais sobre carta e radar; acrescentar a camada de satélite e seus estados.
- `specs/009-mapa-interativo-carta-radar/` — mantém os gates obrigatórios para qualquer camada raster WAC; não habilitar WAC raster nesta mudança.

## Tasks & Acceptance

**Execution:**
- [ ] `servidor/tempo.py` — Resolver o frame REDEMET `realcada` mais recente e validar URL HTTPS, horário e limites antes de devolver os metadados.
- [ ] `app.py` — Expor os metadados por endpoint autenticado, limitado ao piloto dono do plano, sem persistir a imagem nem incluir a chave na resposta.
- [ ] `templates/plano.html`, `static/css/input.css`, `static/css/tailwind.css` — Adicionar o controle de satélite sob demanda, manter radar independente, sempre renderizar a opção WAC com estado disponível/indisponível e tornar o mapa quadrado no desktop.
- [ ] `tests/test_tempo.py`, `tests/test_tela_piloto.py` — Cobrir resposta válida/inválida da API, autorização do plano, ausência de chave exposta, visibilidade WAC e proporção responsiva com casos focados.
- [ ] `documentacao/piloto.md` — Explicar a camada REDEMET, horário do frame e comportamento quando indisponível.

**Acceptance Criteria:**
- Dada uma janela de 390 px ou 1440 px, quando o mapa é exibido, então mantém o layout móvel atual ou tem proporção 1:1 no desktop, respectivamente.
- Dada uma resposta REDEMET válida, quando o piloto ativa Satélite, então o frame mais recente aparece sobre o mapa com horário/fonte, sem alterar rota ou radar; sem resposta válida, não desenha imagem e informa indisponibilidade.
- Dado um plano sem carta AISWEB utilizável, quando o mapa é aberto, então “Carta WAC” continua visível, desabilitada e identificada como indisponível; nenhum mapa de ruas ou PDF é apresentado como camada WAC.
- Dado um plano com documentos WAC AISWEB válidos, quando o piloto seleciona “Carta WAC”, então os documentos oficiais continuam acessíveis pelo diálogo atual.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

O endpoint público documentado pela REDEMET para o produto `realcada` fornece imagens, data/hora e caixa `lat_lon`; a consulta autenticada deve permanecer no servidor. Desenhar a imagem em um pane próprio abaixo da rota preserva a legibilidade dos pontos e permite manter o radar independente. O botão WAC de documento não significa que a carta esteja georreferenciada: os gates já registrados em `specs/009-mapa-interativo-carta-radar/` continuam obrigatórios para uma futura camada WAC raster.

## Verification

**Commands:**
- `uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py -k 'satelite or mapa or wac'` -- testes focados da mudança passam.
- `npm run css:build` -- CSS gerado contém as classes responsivas do mapa.
- `git diff --check` -- nenhuma falha de whitespace.

**Manual checks:**
- Confirmar quadro 1:1 em 1440 px, altura móvel preservada em 390 px, controles por teclado/toque, horário e atribuição REDEMET e estados WAC/satélite indisponíveis.
