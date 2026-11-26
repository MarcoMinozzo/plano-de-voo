---
description: "Tarefas para redesenhar o menu principal"
---

# Tasks: Redesenho do menu principal

**Input**: Design documents from `specs/021-redesenho-menu-principal/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Cobrir apresentação do cabeçalho, navegação e ação de impressão no card de resumo.

## Path Conventions

- Aplicação Flask/Jinja no repositório: `templates/`, `static/` e `tests/`.

## Phase 1: Setup

**Purpose**: A estrutura de aplicação, CSS e testes já existe; nenhuma inicialização é necessária.

## Phase 2: Foundational

**Purpose**: Não há infraestrutura bloqueadora.

## Phase 3: User Story 1 - Navegar e imprimir um plano (Priority: P1) 🎯 MVP

**Goal**: Reorganizar o menu autenticado e deixar a impressão dentro do primeiro card do plano.

**Independent Test**: Testar cabeçalho autenticado em `/planos/novo`, painel e detalhe do plano; verificar logo, dimensões, quatro itens, ausência de overflow e posição da ação de PDF.

### Tests for User Story 1

- [x] T001 [US1] Atualizar `tests/test_casca_visual.py` para verificar logo de 108 px, card central de 70%, itens em maiúsculas, ausência de impressão global e link de PDF dentro de `#resumo`; confirmar falha antes da implementação.

### Implementation for User Story 1

- [x] T002 [P] [US1] Em `templates/base.html` e `static/css/input.css`, separar o logo de 108 px do card semitransparente de navegação, centralizar o card com 70% da viewport, exibir NOVO VOO, VOOS PLANEJADOS, PERFIL e SAIR, preservar URLs/POST e remover impressão global e estilos `#sem-voo`.
- [x] T003 [P] [US1] Em `templates/plano.html`, remover a impressão do bloco de menu e colocar “IMPRIMIR VOO” dentro do primeiro card `#resumo`, apontando para o PDF do plano atual.
- [x] T004 [US1] Executar `npm run css:build` e os testes focados de `tests/test_casca_visual.py` e `tests/test_tela_piloto.py`; corrigir falhas diretamente relacionadas ao novo menu.

**Checkpoint**: O menu e a ação de impressão funcionam nas páginas autenticadas sem alterar o fluxo do plano.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **User Story 1 (Phase 3)**: independente.

### User Story Dependencies

- **US1 (P1)**: sem dependência de outra história.

### Within User Story 1

- T001 precede as alterações.
- T002 e T003 editam arquivos distintos e podem ocorrer em paralelo após T001.
- T004 depende de T002 e T003.

### Parallel Opportunities

- Após T001, executar T002 e T003 em paralelo.

## Parallel Example: User Story 1

```text
Primeiro T001 e confirme a falha esperada.
Depois, em paralelo:
T002: redesenhar a navegação em templates/base.html e static/css/input.css
T003: mover a impressão para templates/plano.html
Finalize com T004.
```

## Implementation Strategy

1. Entregar a única história P1 como MVP.
2. Preservar os endpoints existentes e manter saída por POST.
3. Compilar o CSS e validar viewports e a rota de PDF.
