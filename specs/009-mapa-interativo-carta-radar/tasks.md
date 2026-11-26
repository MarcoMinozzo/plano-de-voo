---
description: "Tarefas de implementação do mapa interativo com carta e radar"
---

# Tasks: Mapa interativo com carta e radar

**Input**: Design documents from `specs/009-mapa-interativo-carta-radar/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: Incluídos porque os cenários independentes e critérios de aceitação da spec exigem validar estados disponíveis, indisponíveis e acesso por piloto.

**Organization**: O gate da fonte da carta antecede sua implementação. A história de meteorologia permanece funcionalmente independente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem conflito de arquivos ou dependências pendentes
- **[Story]**: história relacionada (`US1`, `US2`)
- Cada tarefa indica os caminhos exatos envolvidos

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: Preparação do projeto.

Dependências, Leaflet, configuração Flask e banco já existem. Nenhuma tarefa de setup ou nova dependência é necessária.

---

## Phase 2: Foundational

**Purpose**: Pré-requisitos compartilhados que bloqueiem as histórias.

As colunas JSON, a autenticação de piloto e a resolução de rota existentes atendem à base compartilhada. Não criar migração nem alterar cálculo.

---

## Phase 3: Gate da carta WAC

**Purpose**: Validar se a candidata GeoPDF pode ser usada legal e tecnicamente antes de implementar ou declarar disponível a carta.

**Gate**: Não iniciar tarefas de implementação da carta se algum pré-requisito falhar ou permanecer sem evidência. Não contornar bloqueios de acesso nem substituir a fonte sem nova decisão.

- [ ] T001 Obter o PDF GeoPDF da edição oficial vigente que se aplica à rota e registrar fonte, edição e data em `specs/009-mapa-interativo-carta-radar/research.md`.
- [ ] T002 Validar georreferenciamento do arquivo exato e confirmar que sua cobertura inclui todos os pontos da rota; registrar evidências em `research.md`.
- [ ] T003 Confirmar em termos oficiais que conversão, cache e disponibilização dos tiles derivados são permitidos; guardar referência verificável em `research.md`.
- [ ] T004 Após T002 e T003, demonstrar geração reproduzível de tiles em ambiente compatível, sem executar conversão durante cálculo ou abertura do plano; registrar versões, comando e resultado em `research.md`.
- [ ] T005 Se T001–T004 passarem, decidir e documentar armazenamento, atualização por edição e entrega dos tiles; revisar `plan.md`, `data-model.md`, `contracts/camadas-do-mapa.md` e `quickstart.md` antes de liberar implementação da carta.

## Phase 4: User Story 1 - Escolher camadas do mapa (Priority: P1)

**Prerequisite**: T001–T005 concluídas. Se o gate falhar, manter a carta indisponível e não executar as tarefas de implementação da camada.

**Goal**: Alternar entre ruas e carta visual, com radar inicialmente desligado e independente da base, mantendo rota e zoom.

**Independent Test**: Com os tiles autorizados e simulados e rota válida, alternar as bases, ligar/desligar radar em ambas e confirmar rota preservada; validar indisponibilidade sem fallback.

### Tests for User Story 1

- [ ] T006 [US1] Adicionar testes para disponibilidade/indisponibilidade da carta, propriedade do plano, estado inicial das camadas, radar desligado e falha sem troca silenciosa em `tests/test_tela_piloto.py`. **Parcial/bloqueado**: indisponibilidade, propriedade e radar desligado têm cobertura; disponibilidade da WAC depende dos gates externos T001–T005, ainda pendentes.

### Implementation for User Story 1

- [ ] T007 [US1] Implementar o serviço e a entrega dos tiles locais conforme o plano revisado após os gates, sem converter durante cálculo ou abertura do plano.
- [ ] T008 [US1] Integrar em `templates/plano.html` controles acessíveis de ruas/carta/radar, iniciar radar desligado, preservar rota/zoom e indicar indisponibilidade explícita em falha.

**Checkpoint**: A carta só pode ser declarada funcional com todos os gates aprovados e tiles da edição correta; sem isso, manter indisponível.

## Phase 5: User Story 2 - Consultar meteorologia (Priority: P2)

**Goal**: Organizar METAR/TAF por aeródromo e tipo, mantendo texto bruto, campos e procedência disponíveis.

**Independent Test**: Com dados simulados disponíveis e ausentes, verificar rótulos, fonte/horário, valores fornecidos e indisponibilidade sem inferência.

### Tests for User Story 2

- [X] T009 [US2] **Supersedido por 013/T006–T009**: testes de METAR/TAF estruturado, texto bruto e dados ausentes estão em `tests/test_tempo.py` e `tests/test_tela_piloto.py`; suíte completa passou.

### Implementation for User Story 2

- [X] T010 [US2] **Supersedido por 013/T007–T009**: boletins são apresentados por trecho/aeródromo, preservam o original e indicam campos ausentes; os testes de tela, tempo e PDF passaram.

**Checkpoint**: US2 deve apresentar boletins sem alterar seus dados ou interpretação.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentação e validação final das histórias.

- [X] T011 [P] Atualizar `documentacao/piloto.md` para explicar controles de base, radar inicialmente desligado e indisponibilidade explícita. **Verificado**: documentação descreve ruas, WAC indisponível, OpenAIP e radar independente/desligado.
- [ ] T012 Executar `uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py`, `git diff --check` e os cenários em `specs/009-mapa-interativo-carta-radar/quickstart.md`; corrigir regressões. **Parcial**: suíte completa (136 testes) e `git diff --check` passaram; cenários manuais do quickstart seguem pendentes.
- [ ] T013 Validar em 390 px e 1440 px, por teclado e toque, o foco, zoom, alternância, radar e avisos conforme `specs/009-mapa-interativo-carta-radar/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; sem tarefa.
- **Foundational (Phase 2)**: já atendido; sem tarefa compartilhada ou migração.
- **Gate da carta (Phase 3)**: T001 → T002 e T003; T004 depende de T002 e T003; T005 depende de todos os gates aprovados. Se algum gate falhar, T007 e a parte de carta de T008 ficam bloqueadas.
- **US1 (Phase 4)**: depende do gate e do plano revisado; T006 precede T007/T008.
- **US2 (Phase 5)**: funcionalmente independente do gate da carta; T010 depende de T009. Evitar conflitos com US1 nos arquivos de template e teste compartilhados.
- **Polish (Phase 6)**: depois das histórias implementáveis; T011 pode ocorrer em paralelo com validações, mas T012 e T013 devem validar o resultado integrado.

### User Story Dependencies

- **US1 (P1)**: bloqueada para declarar WAC pronta até validar todos os gates e revisar o plano de entrega dos tiles.
- **US2 (P2)**: funcionalmente independente do gate da carta.

### Within Each User Story

- Testes precedem implementação.
- Os testes e a implementação de METAR/TAF não alteram dados nem interpretação dos boletins.

### Parallel Opportunities

- T002 e T003 podem avançar em paralelo após T001; T004 depende de ambos.
- T009 pode avançar independentemente do gate da carta.
- Não paralelizar tarefas que editam `templates/plano.html` ou `tests/test_tela_piloto.py`.

## Implementation Strategy

1. Validar os quatro gates da GeoPDF e registrar evidências.
2. Se todos passarem, decidir e documentar como armazenar, atualizar e servir os tiles antes de implementar.
3. Se algum gate falhar, manter a carta indisponível e não implementar substituto.
4. Implementar os controles e validar radar/rota sem alterar cálculos; a US2 pode seguir independentemente.

## Notes

- [P] indica arquivos sem conflito e sem dependência pendente.
- Aquisição, validação e conversão de carta nunca participam do cálculo da rota.
- Nenhuma tarefa altera fórmulas, PDF, schema do banco ou dependências.
