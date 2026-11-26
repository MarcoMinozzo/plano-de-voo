---
description: "Tarefas para simplificar a página de detalhes do plano"
---

# Tasks: Enxugar informações da página do plano

**Input**: Design documents from `specs/025-enxugar-pagina-plano/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Uma regressão focada garante que a página fique enxuta sem alterar os avisos do PDF.

## Path Conventions

- Aplicação Flask/Jinja em `templates/`, com testes em `tests/`.

## Phase 1: Setup

**Purpose**: Nenhuma configuração ou dependência nova é necessária.

Nenhuma tarefa.

## Phase 2: Foundational

**Purpose**: O fluxo existente de plano, persistência e PDF permanece inalterado.

Nenhuma tarefa bloqueadora.

## Phase 3: User Story 1 - Consultar um plano sem informações repetitivas (Priority: P1) 🎯 MVP

**Goal**: Remover os blocos solicitados da página de detalhes, preservando alertas, aviso geral didático e PDF.

**Independent Test**: Renderizar um plano sintético e verificar a ausência do estado, aviso extenso, alvo, hipótese de escala e tabela de fontes; confirmar que o PDF mantém a identificação sintética.

### Tests for User Story 1

- [X] T001 [US1] Atualizar a regressão de perfil sintético em `tests/test_rota_pdf.py` para exigir a ausência dos blocos removidos no HTML e preservar aviso e proveniência no PDF.

### Implementation for User Story 1

- [X] T002 [US1] Simplificar a apresentação em `templates/plano.html`, `app.py` e `servidor/pdf_plano.py`, removendo estado, rótulos de perfil e alvo, hipótese de reabastecimento, tabela técnica e subseção sintética da orientação da página, preservando a orientação completa na criação e no PDF.

**Checkpoint**: A página não mostra os blocos solicitados e o PDF continua inalterado.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validar a mudança visual e evitar regressões.

- [X] T003 Executar `uv run pytest -q tests/test_rota_pdf.py` e `git diff --check`, conforme `specs/025-enxugar-pagina-plano/quickstart.md`.

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

Nenhuma: o teste e a implementação seguem TDD e têm dependência sequencial.

## Implementation Strategy

1. Ajustar a regressão em `tests/test_rota_pdf.py` e confirmar que ela falha pelo conteúdo atual da página.
2. Remover somente a apresentação solicitada em `templates/plano.html`.
3. Executar os testes focados e `git diff --check`.

## Notes

- Nenhum dado persistido, cálculo, rota ou conteúdo do PDF deve ser alterado.
- Manter o aviso geral didático e de que o resultado não autoriza voo.
