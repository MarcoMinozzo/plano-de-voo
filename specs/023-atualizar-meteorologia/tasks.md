---
description: "Tarefas para atualizar METAR, TAF e radar ao consultar um plano"
---

# Tasks: Atualizar meteorologia ao consultar o plano

**Input**: Design documents from `specs/023-atualizar-meteorologia/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Incluídos porque a especificação e o plano definem cenários independentes para respostas disponíveis, indisponibilidade, isolamento de falhas e preservação do plano.

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: A aplicação, o ambiente Python e os clientes das fontes já existem; não há setup ou dependência nova.

Nenhuma tarefa.

## Phase 2: Foundational

**Purpose**: Autorização, modelos, banco e serviços meteorológicos existentes atendem à base compartilhada.

Nenhuma tarefa bloqueadora ou migração.

## Phase 3: User Story 1 - Consultar meteorologia atualizada (Priority: P1)

**Goal**: Exibir dados AWC e radar REDEMET atuais ao abrir um plano salvo, mantendo estados indisponíveis explícitos e sem alterar os dados persistidos do plano.

**Independent Test**: Simular uma resposta atual diferente do snapshot salvo; consultar HTML e JSON e confirmar que mostram o resultado atual, preservam rota/cálculos e não repetem consultas ao alternar fichas/camadas.

### Tests for User Story 1

- [X] T001 [P] [US1] Adicionar testes para consulta por aeródromo distinto, METAR/TAF ausente, radar sem chave e falhas isoladas em `tests/test_tempo.py`.
- [X] T002 [P] [US1] Adicionar testes de atualização no detalhe HTML/JSON, ausência de escrita no GET, preservação da rota e indisponibilidade explícita em `tests/test_tela_piloto.py`.

### Implementation for User Story 1

- [X] T003 [US1] Extrair ou adicionar em `servidor/tempo.py` uma consulta de METAR/TAF por aeródromo distinto que possa ser reutilizada por `buscar`, sem solicitar vento ou carta no detalhe do plano.
- [X] T004 [US1] Atualizar `app.py` para consultar meteorologia dos aeródromos dos trechos e radar da rota ao abrir o plano, passando resultados atuais para HTML e JSON sem persistir nem recalcular.
- [X] T005 [US1] Atualizar `templates/plano.html` para consumir os dados atuais de meteorologia e radar recebidos pelo servidor, mantendo indisponibilidade e controles do mapa sem novas consultas.
- [X] T006 [P] [US1] Documentar em `documentacao/piloto.md` que METAR/TAF e radar são consultados ao abrir o plano e podem continuar indisponíveis conforme a fonte.

**Checkpoint**: A história está funcional quando HTML e JSON mostram a resposta atual, mantêm o plano intacto e tratam cada fonte de forma independente.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validar os cenários independentes e a integração documentada.

- [X] T007 Executar `uv run pytest -q tests/test_tempo.py tests/test_tela_piloto.py`, seguir `specs/023-atualizar-meteorologia/quickstart.md` e executar `git diff --check`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **User Story 1 (Phase 3)**: independente; os testes T001/T002 precedem a implementação.
- **Polish (Phase 4)**: T007 depende da implementação e da documentação concluídas.

### User Story Dependencies

- **User Story 1 (P1)**: não depende de outra história.

### Within User Story 1

- T001 e T002 podem executar em paralelo por editarem arquivos de teste diferentes.
- T003 precede T004; T004 precede T005.
- T006 pode executar em paralelo com a implementação por alterar somente documentação.
- T007 executa por último e valida os cenários de integração.

### Parallel Opportunities

```text
T001: testes do serviço em tests/test_tempo.py
T002: testes de tela em tests/test_tela_piloto.py
T006: documentação em documentacao/piloto.md
Depois:
T003 -> T004 -> T005 -> T007
```

## Implementation Strategy

1. Criar os testes focados de serviço e de tela.
2. Reutilizar os serviços existentes para consultar somente METAR/TAF e radar.
3. Atualizar HTML e JSON com dados de cada requisição, sem escrita em GET.
4. Atualizar a orientação do piloto e validar os cenários focados.

## Notes

- `[P]` marca tarefas em arquivos distintos sem dependências pendentes.
- Nenhuma tarefa configura ou solicita segredo REDEMET; sem chave válida o comportamento esperado é indisponibilidade explícita.
