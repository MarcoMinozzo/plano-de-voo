---
description: "Tarefas de implementação da camada aeronáutica OpenAIP"
---

# Tasks: Camada aeronáutica OpenAIP

**Input**: Design documents from `specs/010-camada-openaip/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/tiles-openaip.md`, `quickstart.md`

**Tests**: Incluídos para verificar autorização, proxy, falhas e preservação
da interação do mapa sem depender do serviço remoto.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem conflito de arquivos ou dependências
  pendentes.
- **[Story]**: história relacionada (`US1`).
- Cada tarefa indica os caminhos exatos envolvidos.

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `tests/` e
  `documentacao/`.

## Phase 1: Setup

**Purpose**: Preparação do projeto.

O runtime Flask, Leaflet, requests, autenticação e banco já existem. Nenhuma
tarefa de setup ou nova dependência é necessária.

## Phase 2: Foundational

**Purpose**: Pré-requisitos compartilhados que bloqueiem as histórias.

As sessões e a verificação de propriedade dos planos já existem. Não criar
migração, tabela ou cache persistente.

## Phase 3: User Story 1 - Consultar dados aeronáuticos comunitários (Priority: P1) 🎯 MVP

**Goal**: Selecionar OpenAIP como opção não oficial, com atribuição, sem expor
a chave e preservando rota, base de ruas, carta AISWEB e radar.

**Independent Test**: Com serviço simulado, selecionar OpenAIP e validar
atribuição, tile válido, falha explícita, controle de radar independente,
rota preservada e recusa de acesso ao plano de outro piloto.

### Tests for User Story 1

- [X] T001 [P] [US1] Adicionar testes simulados do serviço para chave ausente, coordenadas inválidas, header de autenticação, tile PNG e respostas remotas inválidas em `tests/test_openaip.py`.
- [X] T002 [P] [US1] Adicionar testes de integração para autenticação, propriedade do plano, estado da camada e HTML com atribuição/controles em `tests/test_tela_piloto.py`.

### Implementation for User Story 1

- [X] T003 [US1] Implementar validação de coordenadas TMS e busca no host fixo OpenAIP, com timeout e chave no header, em `servidor/openaip.py`.
- [X] T004 [US1] Adicionar rota autenticada de tile que verifica a propriedade do plano e não revela detalhes da chave ou do provedor em `app.py`.
- [X] T005 [US1] Adicionar seletor acessível de ruas/OpenAIP, carga explícita dos tiles TMS, atribuição, estados de falha e radar independente em `templates/plano.html`.
- [X] T006 [P] [US1] Declarar `OPENAIP_API_KEY` sem valor em `.env.example`.
- [X] T007 [P] [US1] Documentar configuração da chave, atribuição, licença não comercial e estado indisponível em `documentacao/operacao.md`.
- [X] T008 [P] [US1] Explicar ao piloto que OpenAIP é dado aeronáutico comunitário e não substitui carta WAC em `documentacao/piloto.md`.

**Checkpoint**: A camada é selecionável quando disponível e falha sem fallback
silencioso; os testes não dependem de chave real nem de acesso externo.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validação final da história.

- [X] T009 Executar `uv run pytest --no-cov tests/test_openaip.py tests/test_tela_piloto.py` e `git diff --check`; corrigir regressões relacionadas à feature.
- [ ] T010 Validar `specs/010-camada-openaip/quickstart.md` em 390 px e 1440 px, por teclado e toque, sem exibir credenciais em HTML, URL, mensagens ou logs.
- [X] T011 [P] Atualizar a versão da constituição citada em `.cursor/rules/speckit-sdd.mdc` para corresponder à versão vigente.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; sem tarefa.
- **Foundational (Phase 2)**: já atendido; sem tarefa compartilhada ou migração.
- **User Story 1 (Phase 3)**: independente após as fases existentes; T001 e T002
  precedem as alterações de runtime. T003 e T004 seguem a ordem; T005 depende
  da rota. T006, T007 e T008 podem ocorrer em paralelo com o trabalho de runtime.
- **Polish (Phase 4)**: depende da história implementada.

### User Story Dependencies

- **User Story 1 (P1)**: sem dependência de outra história.

### Within User Story 1

- Testes precedem implementação.
- Serviço precede rota; rota precede integração da interface.
- Configuração e documentação podem ser feitas em paralelo, em arquivos
  distintos.

### Parallel Opportunities

- T001 e T002 podem ser escritos em paralelo.
- T006, T007 e T008 podem ser feitos em paralelo entre si e com T003/T004,
  pois alteram arquivos diferentes.
- Não paralelizar tarefas que editam `app.py`, `servidor/openaip.py` ou
  `templates/plano.html`.

## Parallel Example: User Story 1

```text
Task: T001 — testes simulados do serviço em tests/test_openaip.py
Task: T002 — testes de integração da interface em tests/test_tela_piloto.py
Task: T006 — configuração em .env.example
Task: T007 — operação em documentacao/operacao.md
Task: T008 — orientação do piloto em documentacao/piloto.md
```

## Implementation Strategy

1. Criar os testes simulados e confirmar que falham antes da implementação.
2. Implementar serviço e rota autenticada com segredo somente no servidor.
3. Integrar seletor, tiles TMS, atribuição, falhas explícitas e radar
   independente.
4. Completar documentação e validar a história com a suíte focada.

## Notes

- [P] indica arquivos sem conflito e sem dependência pendente.
- A camada OpenAIP não é uma carta WAC, não substitui AISWEB e não altera o
  cálculo do plano.
- Não usar chave real nos testes nem armazenar tiles em banco ou cache local.
