---
title: "Atualizar meteorologia ao consultar plano"
type: "bugfix"
created: "2026-11-26"
status: "in-progress"
route: "dispatch"
review_loop_iteration: 0
baseline_commit: "90c84f4bd1ca642ae2ac6f3f3edefc703e295690"
context:
  - "{project-root}/.specify/memory/constitution.md"
  - "{project-root}/specs/023-atualizar-meteorologia/spec.md"
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A tela de um plano existente reapresenta os dados meteorológicos guardados quando ele foi criado ou editado, sem consultar novamente as fontes. A chave REDEMET não está carregada na configuração local, então o radar real não pode ser consultado nesse ambiente.

**Approach:** Ao abrir um plano, apresentar resultados atuais do Aviation Weather Center para os aeródromos da rota e da REDEMET para o radar, quando configurada. Manter cada fonte independente e informar indisponibilidade sem inventar dados nem tratar snapshot antigo como atual.

## Boundaries & Constraints

**Always:** Manter AWC como fonte de METAR/TAF e REDEMET como fonte de radar; preservar fonte e horário; manter a indisponibilidade explícita; não alterar cálculos, rota, propriedade ou entradas do plano.

**Never:** Inventar meteorologia ou radar, substituir uma estação sem boletim por outra, gravar chaves no repositório, apresentar snapshot antigo como atual ou fazer chamadas adicionais ao alternar fichas e camadas.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fonte disponível | Plano salvo com aeródromos na rota | Apresentar boletins atuais por aeródromo e radar válido da rota | Uma falha isolada não oculta outras fontes |
| Sem observação METAR | AWC responde sem boletim para um aeródromo | Marcar o METAR daquele aeródromo indisponível | Não usar dado estimado ou de outra estação |
| Chave REDEMET ausente | Configuração local sem chave | Manter radar indisponível e indicar o motivo | Não habilitar sobreposição sem imagem e limites válidos |
| Mudança de ficha/camada | Plano já carregado | Atualizar somente a apresentação do mapa | Não consultar fontes novamente |

</frozen-after-approval>

## Code Map

- `servidor/tempo.py` -- `meteorologia`, `radar` e `buscar` consultam as fontes; os serviços já retornam estado indisponível sem criar dados.
- `servidor/planos.py` -- `montar` grava os snapshots de meteorologia e radar ao criar ou recalcular o plano.
- `app.py` -- `_boletins_por_aerodromo` lê o snapshot do plano; `ver_plano` devolve a página ou JSON sem atualização ao consultar um plano existente.
- `templates/plano.html` -- exibe boletins e usa `plano.radar` para habilitar a camada.
- `tests/test_tempo.py` e `tests/test_tela_piloto.py` -- cobrem serviços e estados da página com fontes simuladas.

## Tasks & Acceptance

**Execution:**
- [ ] `servidor/tempo.py` -- preparar consulta atual de METAR/TAF por aeródromo distinto e radar por rota, reutilizando os serviços existentes.
- [ ] `app.py` -- consultar e apresentar resultados atuais ao abrir o plano em HTML e JSON, sem alterar cálculos ou propriedade.
- [ ] `templates/plano.html` -- mostrar os resultados atuais e a indisponibilidade explícita sem chamadas ao alternar ficha ou camada.
- [ ] `tests/test_tempo.py` e `tests/test_tela_piloto.py` -- validar respostas disponíveis, 204, chave ausente, falha isolada, deduplicação e preservação do plano.

**Acceptance Criteria:**
- Given um plano salvo, when ele é aberto, then os dados apresentados vêm de consultas atuais para cada aeródromo distinto e para o radar da rota, quando a chave existe.
- Given uma fonte sem dados ou indisponível, when o plano é exibido, then essa fonte aparece indisponível sem valores inventados e as demais fontes continuam disponíveis.
- Given a troca de ficha ou camada, when a interface é atualizada, then nenhuma consulta externa adicional é iniciada e os cálculos permanecem intactos.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q tests/test_tempo.py tests/test_tela_piloto.py` -- esperado: testes focados aprovados.
- `git diff --check` -- esperado: nenhuma falha de whitespace.

**Manual checks:**
- Abrir um plano salvo com fontes disponíveis; verificar fonte, horário e dados atuais.
- Abrir um plano sem chave REDEMET; verificar a indisponibilidade explícita e a página funcional.
