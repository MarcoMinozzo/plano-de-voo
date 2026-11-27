---
description: "Tarefas de implementação do mapa quadrado com satélite REDEMET e WAC visível"
---

# Tasks: Mapa quadrado com satélite REDEMET e WAC visível

**Input**: Design documents from `specs/030-mapa-satelite-wac/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Incluídos porque a especificação pede o mínimo de testes focados para fonte, autorização e estados das camadas.

**Organization**: Tarefas agrupadas por história de usuário; preservar ordem de testes antes da implementação.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem conflito de arquivos ou dependências pendentes
- **[Story]**: história relacionada (`US1`, `US2`, `US3`)
- Cada tarefa indica os caminhos exatos envolvidos

## Path Conventions

- Aplicação Flask/Jinja no repositório: `app.py`, `servidor/`, `templates/`, `static/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: Preparar o projeto.

Flask, requests, Leaflet, pytest e o build CSS já existem; não há setup ou dependência nova.

## Phase 2: Foundational

**Purpose**: Pré-requisitos compartilhados.

A autenticação, o acesso ao plano por proprietário e o cliente HTTP com timeout já existem; não há migração nem tarefa fundacional nova.

---

## Phase 3: User Story 1 - Consultar imagem de satélite (Priority: P1) 🎯 MVP

**Goal**: Ativar sob demanda a imagem REDEMET mais recente, com fonte/horário, sem alterar rota ou radar.

**Independent Test**: Simular imagem e erro da REDEMET; verificar seleção do frame, limites, acesso pelo proprietário e estado da camada.

### Tests for User Story 1

- [X] T001 [P] [US1] Testar seleção do frame mais recente, chave ausente/falha remota e rejeição de URL, horário ou limites inválidos em `tests/test_tempo.py`.
- [X] T002 [P] [US1] Testar sessão, propriedade do plano, estado indisponível, ausência da chave e controle inicial de satélite em `tests/test_tela_piloto.py`.

### Implementation for User Story 1

- [X] T003 [US1] Implementar resolvedor REDEMET `realcada` em `servidor/tempo.py`, usando `REDEMET_API_KEY`, selecionando o frame mais recente válido e validando host HTTPS, horário e limites.
- [X] T004 [US1] Adicionar `GET /planos/<int:plano_id>/camadas/satelite` em `app.py`, verificando sessão e proprietário antes da consulta e retornando o contrato de `specs/030-mapa-satelite-wac/contracts/camadas-satelite.md`.
- [X] T005 [US1] Integrar botão Satélite e overlay sob demanda em `templates/plano.html`, com pane abaixo da rota, estado acessível e remoção isolada sem alterar radar ou plano.

**Checkpoint**: Satélite inicia desligado; resposta válida mostra a imagem REDEMET com horário; falha não desenha imagem nem expõe a chave.

---

## Phase 4: User Story 2 - Encontrar e consultar a carta WAC (Priority: P1)

**Goal**: Manter a opção Carta WAC visível, ativa somente para documentos AISWEB válidos e explicitamente indisponível nos demais casos.

**Independent Test**: Renderizar plano com documentos e plano sem documentos; confirmar estado do controle e preservação do diálogo oficial.

### Tests for User Story 2

- [X] T006 [US2] Testar controle WAC visível e desabilitado sem carta, e acionável com documentos AISWEB, em `tests/test_tela_piloto.py`.

### Implementation for User Story 2

- [X] T007 [US2] Ajustar `templates/plano.html` para sempre renderizar Carta WAC, desabilitar e anunciar indisponibilidade sem documentos e preservar o diálogo/link quando disponíveis; não criar camada raster.

**Checkpoint**: A opção nunca desaparece e não identifica ruas ou PDFs como camada WAC georreferenciada.

---

## Phase 5: User Story 3 - Usar o mapa em telas grandes e pequenas (Priority: P2)

**Goal**: Tornar o quadro quadrado no desktop e manter a experiência móvel atual.

**Independent Test**: Conferir proporção 1:1 em 1440 px e controles utilizáveis em 390 px.

### Implementation for User Story 3

- [X] T008 [US3] Definir proporção 1:1 apenas em desktop em `static/css/input.css` para `#mapa` e regenerar `static/css/tailwind.css` pelo script CSS existente.

**Checkpoint**: A altura do mapa corresponde à largura em desktop e a altura móvel não muda.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentar e verificar a mudança integrada.

- [X] T009 [P] Atualizar `documentacao/piloto.md` para explicar a camada de satélite, fonte/horário e estado indisponível, além da opção WAC visível.
- [X] T010 Executar os testes focados, build CSS e `git diff --check`; verificar no navegador os tamanhos 390 px e 1440 px conforme `specs/030-mapa-satelite-wac/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa.
- **US1 (Phase 3)**: testes T001/T002 precedem serviço, rota e interface T003–T005.
- **US2 (Phase 4)**: T006 precede T007; usa o mesmo template de US1 e portanto vem depois de T005.
- **US3 (Phase 5)**: CSS é independente de dados/servidor; executar após as mudanças de template para evitar concorrência com o build de CSS.
- **Polish (Phase 6)**: T009 pode ocorrer em paralelo; T010 depende de todas as histórias.

### User Story Dependencies

- **US1 (P1)**: independente; entrega o overlay REDEMET funcional.
- **US2 (P1)**: funcionalmente independente, mas sequenciada após US1 porque ambos alteram `templates/plano.html`.
- **US3 (P2)**: não depende do serviço de satélite; sequenciada para validar o mapa já integrado.

### Parallel Opportunities

- T001 e T002 editam arquivos de teste diferentes e podem ser feitos em paralelo.
- T009 edita apenas documentação e pode ser feito em paralelo com implementação.
- Não paralelizar tarefas que editam `templates/plano.html`, `tests/test_tela_piloto.py` ou o CSS gerado.

## Implementation Strategy

1. Implementar US1 como MVP, com testes de serviço e autorização antes do código.
2. Adicionar estado WAC explícito, preservando apenas os links oficiais existentes.
3. Ajustar proporção no desktop e regenerar CSS.
4. Atualizar documentação e rodar somente testes focados, build CSS, verificação de diff e checagem visual prevista.

## Phase 7: Convergence

- [X] T011 Validar visualmente a proporção do mapa em 1440 px e os controles sem rolagem horizontal em 390 px conforme SC-001 e SC-002 (partial)
