# Tasks: Priorizar TAF da REDEMET

**Input**: Design documents from `specs/031-taf-redemet/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/taf-meteorologia.md`

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

Nenhuma tarefa de setup: a aplicação Flask, o cliente HTTP e as configurações já existem.

## Phase 2: Foundational

**Purpose**: Blocking prerequisites for user stories

Nenhuma tarefa fundacional: a feature reutiliza a estrutura meteorológica existente e não altera banco ou dependências.

## Phase 3: User Story 1 - Consultar o TAF disponível da REDEMET (Priority: P1)

**Goal**: Exibir o TAF válido mais recente da REDEMET por aeródromo, mantendo AWC como fallback para o mesmo ICAO e preservando METAR independente.

**Independent Test**: Simular REDEMET e AWC para o mesmo aeródromo e verificar mensagem, fonte e validade na página e no PDF; cobrir falhas, indicativo divergente e indisponibilidade total.

### Tests for User Story 1

- [X] T001 [P] [US1] Adicionar testes em `tests/test_tempo.py` para priorizar o TAF REDEMET válido mais recente do mesmo ICAO, fazer fallback AWC e preservar METAR diante de falhas TAF.
- [X] T002 [P] [US1] Adicionar testes em `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py` para confirmar que a fonte e os horários publicados do TAF são apresentados na página e no PDF.

### Implementation for User Story 1

- [X] T003 [US1] Implementar consulta, validação e seleção do TAF REDEMET com fallback AWC para o mesmo indicativo em `servidor/tempo.py`.
- [X] T004 [US1] Incluir emissão e validade publicadas do TAF nos metadados da fonte do relatório em `servidor/planos_consulta.py`, preservando snapshots antigos e fontes AWC.
- [X] T005 [US1] Atualizar a descrição de `REDEMET_API_KEY` para incluir consulta TAF em `documentacao/operacao.md`.

**Checkpoint**: TAF REDEMET deve aparecer identificado quando válido; fallback AWC, METAR e dados de outros aeródromos permanecem independentes.

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T006 Executar os cenários do `specs/031-taf-redemet/quickstart.md` e conferir `git diff --check`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup**: sem tarefas; estrutura existente.
- **Foundational**: sem tarefas; nenhuma infraestrutura bloqueante.
- **User Story 1**: independente após a especificação e o contrato.
- **Polish**: depende da implementação de US1.

### User Story Dependencies

- **US1 (P1)**: pode ser implementada independentemente; única história desta feature.

### Within User Story 1

- T001 e T002 são testes independentes em arquivos distintos e podem ser preparados em paralelo.
- T003 e T004 dependem do formato de saída estabelecido pelos testes e contrato.
- T005 pode ocorrer em paralelo com T003/T004.
- T006 executa após todos os itens anteriores.

## Parallel Example: User Story 1

```text
Task: T001 — testes de seleção e fallback em tests/test_tempo.py
Task: T002 — testes de apresentação em tests/test_tela_piloto.py e tests/test_rota_pdf.py
Task: T005 — documentação da chave em documentacao/operacao.md
```

## Implementation Strategy

1. Implementar apenas US1, começando pelos testes focados de seleção e fallback.
2. Adicionar a consulta REDEMET e validar ICAO, mensagem e horários antes de usar o resultado.
3. Conferir fonte e validade na tabela de fontes da página e do PDF.
4. Rodar os testes focados indicados no `quickstart.md`; não adicionar dependências nem migrações.

## Notes

- [P] indica arquivos independentes sem dependências de tarefas incompletas.
- O TAF nunca pode ser atribuído a outro aeródromo.
- Falha TAF não pode apagar METAR válido nem impedir a abertura do plano.
