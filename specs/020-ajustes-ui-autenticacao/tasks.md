---
description: "Tarefas para aprimorar os cartões de autenticação"
---

# Tasks: Aprimorar cartões de autenticação

**Input**: Design documents from `specs/020-ajustes-ui-autenticacao/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Incluir testes visuais focados e manter a regressão de login existente.

**Organization**: Uma história de usuário P1 para as duas telas públicas de autenticação.

## Path Conventions

- Aplicação Flask/Jinja no repositório: `templates/`, `static/` e `tests/`.

## Phase 1: Setup

**Purpose**: Dependências, runtime e estrutura de testes já existem; nenhuma inicialização é necessária.

## Phase 2: Foundational

**Purpose**: Nenhum pré-requisito de infraestrutura bloqueia a história; autenticação existente será preservada.

## Phase 3: User Story 1 - Acessar e criar uma conta com cartões equilibrados (Priority: P1) 🎯 MVP

**Goal**: Apresentar cartões centralizados com logos maiores, atribuição no login e controles equilibrados sem alterar os formulários.

**Independent Test**: Executar os testes de `tests/test_casca_visual.py` e `tests/test_acesso.py`; conferir `/entrar` e `/cadastro` em 390 px e 1440 px, incluindo espaço para rolagem vertical em viewport baixa.

### Tests for User Story 1

- [x] T001 [US1] Em `tests/test_casca_visual.py`, verificar dimensões dos logos, centralização, ausência do título visível “Entrar”, botão “Acessar”, frase de direitos e espaço reforçado antes do botão; confirmar que falha antes da implementação.

### Implementation for User Story 1

- [x] T002 [US1] Em `templates/base.html`, expor blocos para ocultar o cabeçalho vazio nas telas públicas e aplicar classes de centralização ao conteúdo sem mudar telas autenticadas.
- [x] T003 [P] [US1] Em `templates/entrar.html`, aumentar o logo para 155,52 px, remover visualmente o título “Entrar” mantendo título acessível “Acessar”, renomear o botão, adicionar o espaço solicitado e a frase de direitos abaixo do link “Criar acesso”.
- [x] T004 [P] [US1] Em `templates/cadastro.html`, aumentar o logo para 129,6 px e centralizar o cartão sem alterar campos, validação ou envio.
- [x] T005 [US1] Executar `npm run css:build` para atualizar `static/css/tailwind.css` após mudanças de classes.
- [x] T006 [US1] Executar os testes focados e as inspeções de `specs/020-ajustes-ui-autenticacao/quickstart.md`; corrigir qualquer overflow ou corte observado em `templates/base.html`, `templates/entrar.html` ou `templates/cadastro.html`.

**Checkpoint**: Os dois cartões estão centralizados e os formulários continuam funcionais; o login apresenta a composição aprovada.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **User Story 1 (Phase 3)**: independente; entregar e validar as duas páginas como um incremento.

### User Story Dependencies

- **US1 (P1)**: sem dependência de outra história.

### Within User Story 1

- T001 precede todas as alterações para validar a regressão.
- T002 precede T003 e T004 porque os templates de autenticação dependem dos blocos de layout.
- T003 e T004 podem ser executadas em paralelo após T002, pois editam templates distintos.
- T005 depende de T003 e T004; T006 depende de toda a implementação.

### Parallel Opportunities

- Depois de T002, executar T003 e T004 em paralelo.

## Parallel Example: User Story 1

```text
Primeiro T001 e confirme a falha esperada.
Depois de T002, execute em paralelo:
T003: aplicar composição no login em templates/entrar.html
T004: ajustar logo do cadastro em templates/cadastro.html
Finalize em sequência com T005 e T006.
```

## Implementation Strategy

1. MVP: completar a única história de usuário, começando pelos testes de apresentação.
2. Preservar todos os handlers e contratos de autenticação; não alterar servidor ou banco.
3. Compilar Tailwind e validar testes e viewports conforme o quickstart.
