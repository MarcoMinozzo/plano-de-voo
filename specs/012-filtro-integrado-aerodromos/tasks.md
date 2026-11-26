---
description: "Tarefas para integrar busca e seleção de aeródromos"
---

# Tasks: Filtro integrado na seleção de aeródromos

**Input**: Design documents from `specs/012-filtro-integrado-aerodromos/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/selecao-aerodromo.md`, `quickstart.md`

**Tests**: Requeridos pela especificação para busca, seleção, envio e acessibilidade.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem conflito de arquivos ou dependências.
- **[Story]**: história relacionada (`US1`).
- Cada tarefa indica o caminho exato.

## Phase 1: Setup

**Purpose**: Preparação do projeto. Ambiente de testes e catálogo já estão configurados; não há setup nem dependência nova.

## Phase 2: Foundational

**Purpose**: Pré-requisitos compartilhados. O formulário autenticado e o catálogo existente já atendem a esta feature; não há infraestrutura bloqueadora.

## Phase 3: User Story 1 - Selecionar aeródromos pelo próprio campo (Priority: P1) 🎯 MVP

**Goal**: Pesquisar e selecionar origem e destino em um campo por aeroporto, sem controles de filtro separados.

**Independent Test**: Abrir o formulário, buscar parte do código e do nome com variações de caixa/acentuação, selecionar opções, tentar texto livre e verificar o identificador enviado.

### Tests for User Story 1

- [X] T001 [US1] Adicionar regressões de marcação, pesquisa parcial sem acentos, seleção de ICAO, texto livre e valores restaurados em `tests/test_tela_piloto.py`.

### Implementation for User Story 1

- [X] T002 [US1] Aprimorar progressivamente os seletores nativos com um campo acessível de pesquisa/seleção para origem e destino, mantendo o fallback sem JavaScript e os ICAOs nos campos existentes em `templates/plano_novo.html`.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Confirmar a regressão e preservar o restante do fluxo.

- [X] T003 Executar `uv run pytest --no-cov tests/test_tela_piloto.py -q` e `git diff --check`; corrigir somente regressões da feature em `tests/test_tela_piloto.py` e `templates/plano_novo.html`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; sem dependências.
- **Foundational (Phase 2)**: já atendido; sem tarefa bloqueadora.
- **User Story 1 (Phase 3)**: T001 precede T002 para validar a mudança pelo teste.
- **Polish (Phase 4)**: T003 depende de T001 e T002.

### User Story Dependencies

- **User Story 1 (P1)**: história única; sem dependência de outra história.

### Parallel Opportunities

- Nenhuma tarefa da implementação é paralelizável: o teste e a interface estão acoplados e devem seguir a ordem T001 → T002 → T003.

## Implementation Strategy

1. Criar os testes de regressão que falham com os controles separados atuais.
2. Implementar os campos combinados sem mudar servidor ou catálogo.
3. Executar a suíte focada e validar busca, seleção e acessibilidade do controle.

## Notes

- Não alterar API, banco, catálogo, regras de rota ou cálculos.
- Preservar todas as alterações locais preexistentes.
