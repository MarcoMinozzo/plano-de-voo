---
description: "Tarefas para integrar RainViewer como camada suplementar de radar"
---

# Tasks: Camada suplementar de radar RainViewer

**Input**: Design documents from `specs/024-camada-radar-rainviewer/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Incluídos para validar manifestação/tiles simulados, autenticação, cobertura e independência da REDEMET antes da integração.

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: A pilha Flask, Leaflet, requests e o banco já existem; não há setup ou dependência nova.

Nenhuma tarefa.

## Phase 2: Foundational

**Purpose**: Reutilizar a autenticação e a verificação de propriedade de plano existentes; não há migração.

Nenhuma tarefa bloqueadora.

## Phase 3: User Story 1 - Consultar radar suplementar (Priority: P1) 🎯 MVP

**Goal**: Oferecer RainViewer como camada opcional, não oficial e separada da REDEMET, com atribuição, horário e cobertura sem confundir ausência de eco com falta de cobertura.

**Independent Test**: Simular manifesto, tiles e máscara; ativar/desativar RainViewer no mapa, verificar que REDEMET, base, rota e cálculos permanecem independentes e que erros são explícitos.

### Tests for User Story 1

- [X] T001 [P] [US1] Testar manifesto/frame, máscara, tiles inválidos, timeout e validação de frame/coordenadas em `tests/test_rainviewer.py`.
- [X] T002 [P] [US1] Testar rotas autenticadas, propriedade do plano, estado independente da REDEMET e controles/atribuição do mapa em `tests/test_tela_piloto.py`.

### Implementation for User Story 1

- [X] T003 [US1] Criar cliente RainViewer com hosts fixos, seleção do frame, validação XYZ, validação de PNG e busca de máscara em `servidor/rainviewer.py`.
- [X] T004 [US1] Adicionar rotas autenticadas e limitadas ao plano para manifesto, tiles de radar e máscara, sem aceitar URLs upstream arbitrárias, em `app.py`.
- [X] T005 [US1] Integrar controles RainViewer desligados inicialmente, proxy same-origin, máscara/legenda de cobertura, atribuição e horário do frame em `templates/plano.html`.
- [X] T006 [P] [US1] Documentar RainViewer como camada suplementar não oficial, limitações de cobertura e termos educacionais em `documentacao/piloto.md`.

**Checkpoint**: A camada é funcional com respostas simuladas, mantém a REDEMET separada e não trata ausência de cobertura como ausência de chuva.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Executar validação focada e conferência manual do provedor.

- [X] T007 Executar `uv run pytest -q tests/test_rainviewer.py tests/test_tela_piloto.py`, seguir `specs/024-camada-radar-rainviewer/quickstart.md` e executar `git diff --check`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **User Story 1 (Phase 3)**: independente; testes T001/T002 precedem a implementação.
- **Polish (Phase 4)**: T007 depende de T003–T006.

### User Story Dependencies

- **User Story 1 (P1)**: não depende de outra história.

### Within User Story 1

- T001 e T002 podem executar em paralelo por editarem arquivos de teste distintos.
- T003 sucede T001; T004 sucede T003 e T002; T005 sucede T004.
- T006 pode executar em paralelo à implementação por alterar somente documentação.
- T007 executa por último.

### Parallel Opportunities

```text
T001: testes do provedor em tests/test_rainviewer.py
T002: testes da rota e tela em tests/test_tela_piloto.py
T006: documentação do piloto em documentacao/piloto.md
Depois:
T003 -> T004 -> T005 -> T007
```

## Implementation Strategy

1. Criar testes de serviço e integração com respostas externas simuladas.
2. Implementar o cliente usando somente hosts RainViewer fixos e dados do manifesto atual.
3. Expor manifesto e tiles por rotas autenticadas que confirmam propriedade do plano.
4. Adicionar o overlay escolhido explicitamente, máscara de cobertura e atribuição visível.
5. Validar o quickstart e confirmar manualmente cobertura e disponibilidade sem declarar garantia operacional.

## Notes

- `[P]` marca tarefas em arquivos distintos sem dependências pendentes.
- Nenhum segredo, dependência, tabela ou campo persistente deve ser adicionado.
- O radar RainViewer não pode alterar nem substituir a camada oficial REDEMET.
