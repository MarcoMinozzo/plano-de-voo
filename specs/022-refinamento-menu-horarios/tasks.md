---
description: "Tarefas para refinar o menu e a exibição dos horários"
---

# Tasks: Refinamento do menu e horários

**Input**: Design documents from `specs/022-refinamento-menu-horarios/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Tests**: Atualizar apenas as verificações visuais existentes necessárias para as mudanças.

## Path Conventions

- Aplicação Flask/Jinja no repositório: `templates/`, `static/` e `tests/`.

## Phase 1: Setup

**Purpose**: A estrutura de aplicação, CSS e testes já existe; nenhuma inicialização é necessária.

## Phase 2: Foundational

**Purpose**: Não há infraestrutura bloqueadora.

## Phase 3: User Story 1 - Navegar com clareza (Priority: P1)

**Goal**: Refinar o logo e a navegação autenticada para telas amplas e estreitas.

**Independent Test**: Inspecionar o cabeçalho em 1440 px e 390 px, confirmando alinhamento, menu central ajustado ao conteúdo, ícones, contraste, botão Sair acessível e ausência de overflow.

- [x] T001 [P] [US1] Refinar logo, navegação desktop/móvel e tokens de texto/cartões em `templates/base.html` e `static/css/input.css`.

## Phase 4: User Story 2 - Ler o horário de partida (Priority: P1)

**Goal**: Mostrar a partida até minutos e identificá-la como tempo local.

**Independent Test**: Abrir o painel e confirmar que a data e hora terminam com “TL” e não exibem segundos.

- [x] T002 [P] [US2] Formatar o horário de partida até minutos com o sufixo “TL” em `templates/painel.html`.

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Atualizar as verificações visuais e validar as duas histórias sem rodar a suíte completa.

- [x] T003 Atualizar as verificações de navegação, cores e horário em `tests/test_casca_visual.py`.
- [x] T004 Compilar `static/css/tailwind.css`, executar `tests/test_casca_visual.py` e verificar `git diff --check`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **US1 e US2**: independentes e podem ser implementadas em paralelo.
- **Polish**: T003 depende de T001 e T002; T004 depende de T003.

### Parallel Opportunities

- Em paralelo: T001 e T002, pois alteram arquivos de apresentação diferentes.
- Sequencial: T003 e depois T004.

## Parallel Example: User Stories

```text
T001: cabeçalho e tokens em templates/base.html e static/css/input.css
T002: horário em templates/painel.html
Depois:
T003: atualizar verificações em tests/test_casca_visual.py
T004: compilar CSS e executar validação focada
```

## Implementation Strategy

1. Implementar as duas histórias P1 como o incremento pedido.
2. Atualizar somente as verificações visuais relacionadas.
3. Executar a compilação, o teste focado e a inspeção manual em dois tamanhos de tela.
