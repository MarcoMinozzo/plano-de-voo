---
description: "Tarefas para centralizar o logo nas telas de login e cadastro"
---

# Tasks: Logo centralizado no login e cadastro

**Input**: Design documents from `specs/016-logo-login-cadastro/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Tests**: Incluir testes visuais focados para posição, dimensão e ausência de duplicação do logo.

## Phase 1: Setup

**Purpose**: Nenhuma dependência ou scaffold novo é necessário.

## Phase 2: Foundational

**Purpose**: Nenhuma infraestrutura compartilhada bloqueia a história.

## Phase 3: User Story 1 - Identificar a aplicação ao entrar ou criar acesso (Priority: P1)

**Goal**: Mostrar o logo centralizado no cartão de autenticação, 20% maior, sem duplicá-lo no cabeçalho dessas telas.

**Independent Test**: Conferir `/entrar` e `/cadastro` em 390 px e 1440 px; cada página mostra o logo de 86,4 px acima do título e nenhuma cópia no cabeçalho. Uma página autenticada mantém o logo no cabeçalho.

### Tests for User Story 1

> Escrever primeiro e confirmar que falham antes da implementação.

- [X] T001 [US1] Adicionar em `tests/test_casca_visual.py` verificações de logo dentro do cartão, centralização, classe de largura correspondente a 86,4 px, ausência no cabeçalho de entrar/cadastro e presença no cabeçalho autenticado.

### Implementation for User Story 1

- [X] T002 [US1] Envolver o logo do cabeçalho em um bloco Jinja substituível em `templates/base.html`, mantendo a imagem padrão nas páginas existentes.
- [X] T003 [US1] Inserir o emblema reutilizado, com proporção preservada, largura de 86,4 px e centralização acima do título em `templates/entrar.html` e `templates/cadastro.html`; ocultar o bloco de logo do cabeçalho somente nessas duas páginas e manter os cartões dentro do viewport.

**Checkpoint**: A posição e dimensão são iguais nas duas telas; páginas autenticadas continuam com o cabeçalho atual.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Verificar compilação, regressão e responsividade conforme `quickstart.md`.

- [X] T004 Executar `npm run css:build`, `uv run --no-sync pytest --no-cov tests/test_casca_visual.py`, `git diff --check` e a inspeção manual de `specs/016-logo-login-cadastro/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** e **Foundational (Phase 2)**: não exigem tarefas.
- **User Story 1 (Phase 3)**: T001 precede T002; T003 depende do bloco definido em T002.
- **Polish (Phase 4)**: T004 depende da conclusão de T001–T003.

### User Story Dependencies

- **User Story 1 (P1)**: independente; entrega o ajuste completo de entrar e cadastro.

### Parallel Opportunities

- Não há tarefas de implementação independentes: os templates de autenticação substituem o bloco definido no template base.

## Parallel Example: User Story 1

```text
Executar T001 primeiro. Depois T002 e T003 em sequência; concluir com T004.
```

## Implementation Strategy

### MVP First

1. Criar os testes de layout em T001.
2. Preservar o logo padrão e permitir sua substituição em T002.
3. Aplicar a composição solicitada nas duas páginas em T003.
4. Validar o cenário completo em T004.

### Incremental Delivery

Entregar somente a User Story 1; não há história independente adicional.
