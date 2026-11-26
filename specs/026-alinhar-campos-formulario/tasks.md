---
description: "Tarefas para alinhar campos do formulário"
---

# Tasks: Alinhar campos do formulário

**Input**: Design documents from `specs/026-alinhar-campos-formulario/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Regressão focada na estrutura e responsividade dos campos é necessária.

## Path Conventions

- Aplicação Flask/Jinja em `templates/`, com testes em `tests/`.

## Phase 1: Setup

**Purpose**: Nenhuma configuração ou dependência nova é necessária.

Nenhuma tarefa.

## Phase 2: Foundational

**Purpose**: Nenhuma alteração compartilhada de infraestrutura ou dados é necessária.

Nenhuma tarefa bloqueadora.

## Phase 3: User Story 1 - Preencher o formulário de voo (Priority: P1) 🎯 MVP

**Goal**: Exibir data/hora e número de passageiros juntos, e peso das pessoas e da bagagem juntos, mantendo o formulário responsivo e sem alterar seu comportamento.

**Independent Test**: Renderizar `/planos/novo` e verificar que cada par usa um grupo de duas colunas responsivo, com os quatro nomes de campo existentes preservados.

### Tests for User Story 1

- [X] T001 [US1] Adicionar teste de regressão em `tests/test_tela_piloto.py` para verificar os dois grupos responsivos e os nomes existentes dos quatro campos.

### Implementation for User Story 1

- [X] T002 [US1] Agrupar os campos data/hora e número de passageiros, e peso das pessoas e peso da bagagem, em linhas responsivas em `templates/plano_novo.html`, mantendo a confirmação de horário junto à data.

**Checkpoint**: Os pares compartilham linha a partir de 640 px, empilham em telas menores e o formulário continua enviando os mesmos valores.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validar a regressão e a formatação final.

- [X] T003 Executar `uv run pytest -q tests/test_tela_piloto.py` e `git diff --check` conforme `specs/026-alinhar-campos-formulario/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **User Story 1 (Phase 3)**: independente.
- **Polish (Phase 4)**: T003 depende de T001 e T002.

### User Story Dependencies

- **User Story 1 (P1)**: não depende de outra história.

### Within User Story 1

- T001 é a regressão inicial e deve falhar antes da mudança de template.
- T002 sucede T001.
- T003 executa após a implementação.

### Parallel Opportunities

Nenhuma: o teste e a implementação afetam os mesmos arquivos do fluxo e seguem TDD.

## Implementation Strategy

1. Criar uma regressão para os dois grupos responsivos e confirmar que ela falha.
2. Alterar somente a estrutura visual de `templates/plano_novo.html`.
3. Executar os testes focados e `git diff --check`.

## Notes

- Não alterar nomes, valores, limites, validações, cálculo, persistência ou processamento dos campos.
