---
description: "Tarefas para aumentar o logo somente na página de login"
---

# Tasks: Aumentar logo no login

**Input**: Design documents from `specs/017-aumentar-logo-login/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Organization**: Tarefas agrupadas pela única história independente da feature.

## Phase 1: Setup

**Purpose**: Nenhuma dependência ou scaffold novo é necessário.

## Phase 2: Foundational

**Purpose**: Nenhuma infraestrutura compartilhada bloqueia a história.

## Phase 3: User Story 1 - Reconhecer a aplicação ao entrar (Priority: P1)

**Goal**: Aumentar somente o logo do cartão de login em 20%, mantendo cadastro e cabeçalhos inalterados.

**Independent Test**: Em `/entrar`, verificar logo com 103,68 px, centralizado e sem overflow; em `/cadastro`, confirmar 86,4 px; numa página autenticada, confirmar que o logo do cabeçalho permanece.

### Tests for User Story 1

> Ajustar a regressão existente primeiro e confirmar que ela falha antes da mudança de template.

- [X] T001 [US1] Atualizar `tests/test_casca_visual.py` para exigir 103,68 px somente em `/entrar`, conservar 86,4 px em `/cadastro` e manter os testes de centralização, cabeçalho, proporção e presença única.

### Implementation for User Story 1

- [X] T002 [US1] Alterar somente a classe de largura do logo no cartão em `templates/entrar.html` para 103,68 px, preservando `h-auto`, centralização, texto alternativo e demais elementos do formulário.

**Checkpoint**: Login usa o novo tamanho; cadastro, cabeçalho autenticado e comportamento dos formulários permanecem inalterados.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validar CSS compilado e apresentação em larguras estreita e larga.

- [X] T003 Executar os comandos de `specs/017-aumentar-logo-login/quickstart.md` e inspecionar `/entrar` em 390 px e 1440 px, confirmando tamanho, centralização, proporção e ausência de overflow.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** e **Foundational (Phase 2)**: não exigem tarefas.
- **User Story 1 (Phase 3)**: T001 precede T002 para validar a regressão antes da implementação.
- **Polish (Phase 4)**: T003 depende de T001 e T002.

### User Story Dependencies

- **User Story 1 (P1)**: independente; entrega integralmente o ajuste solicitado.

### Parallel Opportunities

- Não há paralelismo necessário: primeiro atualiza-se o teste, depois o template correspondente e, por fim, valida-se o resultado integrado.

## Parallel Example: User Story 1

```text
Executar T001 e confirmar a falha; implementar T002; concluir com T003.
```

## Implementation Strategy

### MVP First

1. Ajustar o teste da dimensão diferenciada de login e cadastro em T001.
2. Alterar somente a largura no template de login em T002.
3. Executar os testes, compilar o CSS e validar responsividade em T003.

### Incremental Delivery

Uma única história entrega a mudança completa; não há história adicional independente.
