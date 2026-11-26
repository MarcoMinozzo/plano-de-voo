---
title: 'Restaurar gates de validação'
type: 'bugfix'
created: '2026-11-26'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/.cursor/rules/speckit-sdd.mdc'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A suíte completa deixa quatro falhas: três funções excedem o limite de complexidade, a pontuação de mutação está abaixo do piso e dois testes de tela ainda esperam textos que não correspondem à mensagem atual. O estado das tarefas pendentes também mistura trabalho implementado, gates externos e requisitos DEMO já substituídos.

**Approach:** Restaurar os gates sem alterar o comportamento funcional: refatorar as funções mantendo suas interfaces, alinhar os testes à interface atual, identificar e testar mutações relevantes sem reduzir o piso e reconciliar as tarefas com evidências do código e dos gates.

**Boundaries & Constraints**

**Always:** Preservar cálculo, respostas e mensagens atuais; manter os limites de complexidade 23, tamanho de módulo 462 linhas e mutação 56%; executar testes apenas no banco descartável já confirmado; deixar explícitos os gates externos não concluídos.

**Never:** Alterar regra de cálculo para matar mutantes; reduzir limites; marcar como concluída uma tarefa que dependa de fonte oficial, licença, configuração externa ou validação manual ainda não verificada; editar a interface do logo nesta etapa.

</frozen-after-approval>

## Code Map

- `servidor/proveniencia.py::procedencia_aeronave` -- monta procedência dos seis campos obrigatórios; extrair serialização/aplicação de valores preservando o formato retornado.
- `servidor/catalogo.py::_baixar_rotaer` -- pagina a lista, reaproveita cache e busca detalhes concorrentes; dividir responsabilidades sem mudar fallbacks, progresso, validação ou propagação de erros.
- `servidor/planos.py::montar` -- valida dados, escolhe rota e monta resultado; separar etapas mantendo mensagens, estados e efeitos.
- `templates/plano_novo.html` -- contém as mensagens atuais de indisponibilidade factual e disponibilidade sintética. Os dois testes falhos esperam cópia antiga; atualizar asserções, não a interface.
- `tests/test_tela_piloto.py` -- ajustar os dois casos para confirmar a cópia e o comportamento atuais sem afrouxar a seleção separada dos 20 perfis.
- `servidor/calculo.py`, `tests/test_calculo.py`, `suite/test_mutation_targets.py` e `mutants/` -- alvo de mutação e evidências; a execução anterior reportou cache não atualizado e 52,5%, então confirmar os sobreviventes numa execução atual antes de escolher cobertura.
- `specs/002-rota-com-escalas/tasks.md`, `specs/006-catalogo-demo-sintetico/tasks.md`, `specs/007-proxies-aeronaves-demo/tasks.md`, `specs/009-mapa-interativo-carta-radar/tasks.md`, `specs/010-camada-openaip/tasks.md`, `specs/013-plano-por-trecho/tasks.md` e `specs/revisao-codigo-pronto/tasks.md` -- reconciliar tarefas com implementação, supersessão e gates ainda necessários; não fechar trabalho não verificado.

## Tasks & Acceptance

**Execution:**
- `servidor/proveniencia.py`, `servidor/catalogo.py`, `servidor/planos.py` -- extrair helpers para respeitar complexidade máxima 23 sem alterar interfaces ou resultados.
- `tests/test_tela_piloto.py` -- atualizar somente as duas asserções de texto obsoletas e manter verificações de catálogo vazio e perfis sintéticos.
- `tests/test_calculo.py`, `suite/test_mutation_targets.py` -- classificar mutantes sobreviventes relevantes e acrescentar testes para comportamento definido, sem alterar a regra do cálculo nem o piso.
- `specs/*/tasks.md` indicados no Code Map -- registrar com evidência o que está concluído, bloqueado ou supersedido; preservar itens que dependem de validação futura.

**Acceptance Criteria:**
- Given a suíte completa, when os gates são executados, then os testes funcionais passam e os limites de complexidade e mutação são respeitados sem reduzir seus valores.
- Given os textos atuais da interface, when os testes da tela são executados, then eles verificam a mensagem vigente e a disponibilidade dos perfis sem RAB.
- Given as listas de tarefas, when reconciliadas com o código e a evidência disponível, then nenhuma tarefa bloqueada ou não verificada aparece como concluída e requisitos DEMO supersedidos são identificados.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run --no-sync pytest` -- esperado: suíte aprovada, cobertura mínima satisfeita e gates de revisão verdes.
- `git diff --check` -- esperado: sem erros de whitespace.
