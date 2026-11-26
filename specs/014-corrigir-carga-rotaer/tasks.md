---
description: "Tarefas para corrigir a carga do ROTAER AISWEB"
---

# Tasks: Corrigir carga do ROTAER

**Input**: Design documents from `/specs/014-corrigir-carga-rotaer/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/aisweb-rotaer.md`, `quickstart.md`

**Tests**: Obrigatórios. Usar respostas AISWEB fictícias em testes; não fazer chamadas de rede dentro do pytest.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem dependência de tarefa incompleta.
- **[Story]**: história relacionada (`US1`).
- Cada tarefa indica os caminhos exatos.

## Path Conventions

- Aplicação Flask na raiz: `servidor/`, `alembic/versions/`, `tests/`, `documentacao/`.

## Phase 1: Setup

**Purpose**: Reutilizar `requests`, PostgreSQL e Alembic existentes; não há dependência nova.

## Phase 2: Foundational

**Purpose**: Nenhum pré-requisito adicional; catálogo, sessão do banco e comando de operação já existem.

## Phase 3: User Story 1 - Carregar o catálogo ROTAER vigente (Priority: P1) 🎯 MVP

**Goal**: Interpretar a lista AISWEB atual e carregar todos os aeródromos de avião com detalhe e proveniência completos, sem publicar carga parcial.

**Independent Test**: Simular lista paginada, detalhes por ICAO, falha no detalhe e repetição sem alteração; validar estado, dados e número de chamadas.

### Tests for User Story 1

> Escrever primeiro e confirmar que falham antes da implementação.

- [X] T001 [US1] Adicionar em `tests/test_catalogo_aerodromos.py` fixtures XML para lista AISWEB `<rotaer><item>`, detalhe por ICAO e testes de paginação, validação do total, cache de versão, ICAO incompatível, campos obrigatórios ausentes e ausência de catálogo parcial.

### Implementation for User Story 1

- [X] T002 [US1] Adicionar em `servidor/modelos.py` os campos opcionais `rotaer_versao_id` e `rotaer_atualizado_em` em `Aerodromo`; criar em `alembic/versions/` uma migração aditiva com esses campos nullable para preservar registros legados.
- [X] T003 [US1] Corrigir em `servidor/catalogo.py` a interpretação da lista AISWEB, usando paginação por quantidade, validando o total e selecionando somente registros `AD` com identificador, versão e data publicados.
- [X] T004 [US1] Implementar em `servidor/catalogo.py` a consulta detalhada individual com no máximo quatro solicitações simultâneas, validação de ICAO/posição/elevação, reutilização por versão e data, gravação atômica e diagnóstico/progresso sem credenciais.
- [X] T005 [P] [US1] Atualizar `documentacao/operacao.md` para explicar a primeira carga detalhada, o progresso, a reutilização de versões e a falha sem publicação parcial.
- [X] T007 [US1] Adicionar em `tests/test_catalogo_aerodromos.py` um caso de regressão para detalhe XML vazio e resposta HTML oficial AISWEB com ICAO, tipo, data, coordenadas e elevação.
- [X] T008 [US1] Em `servidor/catalogo.py`, tentar `force=html` quando o XML de detalhe não corresponder ao ICAO; validar e interpretar os campos oficiais, e atualizar `specs/014-corrigir-carga-rotaer/contracts/aisweb-rotaer.md` e `documentacao/operacao.md`.

**Checkpoint**: A lista completa fica disponível somente quando todas as páginas e detalhes obrigatórios foram validados.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validar regressões da carga e consistência do contrato.

- [X] T006 Executar `uv run pytest --no-cov tests/test_catalogo_aerodromos.py -q` e `git diff --check`; corrigir somente falhas relacionadas à carga AISWEB em `servidor/catalogo.py`, `servidor/modelos.py`, `alembic/versions/` e `tests/test_catalogo_aerodromos.py`.
- [X] T009 Reexecutar `uv run pytest --no-cov tests/test_catalogo_aerodromos.py -q` e `git diff --check` após o fallback de detalhes.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; sem dependências.
- **Foundational (Phase 2)**: já atendido; sem tarefa bloqueadora.
- **US1 (Phase 3)**: T001 precede T002; T002 precede T003 e T004; T003 precede T004. T005 pode ocorrer em paralelo depois de T001.
- **Polish (Phase 4)**: T006 depende de T001–T005.

### User Story Dependencies

- **US1 (P1)**: história única; sem dependência de outra história.
- **Correção de detalhe vazio**: T007 → T008 → T009; a regressão deve existir antes do fallback e a suíte deve passar depois.

### Parallel Opportunities

- T005 altera somente documentação e pode ocorrer em paralelo com T002–T004 após os testes T001.
- As alterações de modelo, migração e catálogo são sequenciais para manter o esquema e o cache coerentes.

## Implementation Strategy

1. Criar os testes simulados e verificar a falha contra o parser atual.
2. Persistir versão/data da fonte e criar a migração aditiva.
3. Implementar leitura paginada, consulta detalhada limitada e cache de versões.
4. Confirmar que erros e carga parcial nunca resultam em catálogo disponível.
5. Executar testes direcionados e a verificação de whitespace; não fazer carga nacional real nos testes.
