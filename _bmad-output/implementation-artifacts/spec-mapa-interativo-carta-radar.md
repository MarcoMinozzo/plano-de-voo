---
title: 'Carta WAC como camada do mapa'
type: 'feature'
created: '2026-11-25'
status: 'draft'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/009-mapa-interativo-carta-radar/spec.md'
  - '{project-root}/specs/009-mapa-interativo-carta-radar/plan.md'
  - '{project-root}/_bmad-output/planning-artifacts/research/technical-verificar-georreferenciamento-da-carta-w-2026-11-25/research.md'
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

## Open Questions

- **Fonte e regra de produto** — OpenAIP oferece tiles aeronáuticos PNG/PBF licenciados CC BY-NC 4.0, mas não uma WAC oficial; a constituição atual determina AISWEB como fonte da carta visual. Opções: manter essa regra e aguardar autorização AISWEB (sem camada até lá) / pedir alteração explícita da constituição para permitir uma camada OpenAIP claramente rotulada como dado aeronáutico comunitário, não como WAC, com atribuição, cumprimento CC BY-NC e chave de API configurada (camada diferente da carta oficial).

## Code Map

- `servidor/tempo.py:carta` — consulta a API AISWEB autenticada, escolhe WAC cuja caixa cobre origem/destino e devolve apenas URL/fonte; não baixa nem georreferencia o PDF.
- `servidor/planos.py` — persiste `carta` e `radar` como JSON no plano.
- `app.py` — resolve pontos da rota publicada e passa-os ao template; consulta do plano já filtra por piloto.
- `templates/plano.html` — Leaflet usa OSM fixo e adiciona o radar automaticamente; a carta atual é apenas um link documental.
- `tests/test_tempo.py`, `tests/test_tela_piloto.py` — mocks AISWEB e validação da tela; estender para metadados/estados de carta e interação das camadas.
- `documentacao/operacao.md` — descreve credenciais AISWEB; nesta sessão elas não estão configuradas e não há GeoPDF em `static/`.
- `specs/009-mapa-interativo-carta-radar/` — critérios e tarefas já condicionam a implementação aos gates da carta; manter alinhados antes de alterar o runtime.

## Tasks & Acceptance

**Execution:**
- [ ] Validar o GeoPDF da edição atual, georreferenciamento, cobertura completa, autorização oficial e geração reproduzível de tiles; registrar evidências antes de habilitar a camada.
- [ ] Atualizar a spec, o plano e as tarefas do Spec Kit com o armazenamento/versionamento autorizado dos tiles e o contrato da camada.
- [ ] Integrar a base WAC selecionável e os controles de ruas/radar no Leaflet, sem alterar cálculo, geometria ou propriedade do plano.
- [ ] Cobrir carta disponível/indisponível, tile com falha, radar independente e rota preservada nos testes; atualizar a documentação do piloto.

**Acceptance Criteria:**
- Dado um tilepack oficial autorizado, vigente e que cobre toda a rota, quando o piloto seleciona Carta, então vê a WAC alinhada, com fonte/edição identificáveis, rota preservada e radar controlável.
- Dado um gate não comprovado ou tile inválido, quando o plano abre ou a carta é selecionada, então a carta aparece indisponível e ruas não são apresentadas como carta.
- Dado qualquer mudança de base ou radar, quando a rota está visível, então seus pontos permanecem inalterados e o mapa continua utilizável por toque e teclado.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

A aplicação já busca URL WAC na API AISWEB, mas isso não fornece uma camada cartográfica pronta. A inspeção anterior confirmou georreferenciamento somente em uma carta de 2020; a tentativa local de gerar tiles falhou por incompatibilidade GDAL/NumPy. A busca da política oficial AISWEB indica restrições de uso do conteúdo, com exceções sujeitas a regulamentação/autorização; a página direta retornou 403 nesta sessão. A OpenAIP oferece uma camada de dados aeronáuticos licenciada, mas não é uma carta WAC e usar outra fonte exige alterar a regra vigente da constituição. Nenhum dado antigo ou derivado será publicado sem validação e autorização.

## Verification

**Commands:**
- `uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py` -- testes focados aprovados.
- `git diff --check` -- nenhuma falha de whitespace.

**Manual checks:**
- Confirmar edição e cobertura da carta, alinhamento com pontos da rota, controles por toque/teclado em 390 px e 1440 px, falha explícita sem fallback e autorização documentada para os tiles.
