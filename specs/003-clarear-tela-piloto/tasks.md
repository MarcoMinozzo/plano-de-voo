---

description: "Task list for clarear a tela do piloto"
---

# Tasks: Clarear a tela do piloto

**Input**: Design documents from `/specs/003-clarear-tela-piloto/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tela-piloto.md, quickstart.md, constitution 2.2.0

**Tests**: Incluídos, no mesmo cliente Flask das features anteriores. A lista nacional real não entra no pytest.

**Organization**: Uma história por fase, na ordem da spec. A conta da rota não muda.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode correr em paralelo (outro arquivo, sem depender de tarefa incompleta)
- **[Story]**: História da spec (US1…US7)
- Cada tarefa cita o arquivo que altera

## Path Conventions

Aplicação Flask na raiz: `app.py`, `templates/`, `servidor/`, `tests/`.

## Phase 1: Setup

**Purpose**: Confirmar que a feature não pede biblioteca nova

- [X] T001 Conferir que `requirements.txt` não ganha pacote: a busca usa o Flask e o SQLAlchemy já fixados

## Phase 2: Foundational

**Purpose**: Rótulo de leitura e busca curta, usados por mais de uma história

- [X] T002 Acrescentar `rotulo_lido` em `servidor/planos.py`: `calculado` lê "aceitável para planejamento", `inaceitavel` lê "não aceitável", `indisponivel` lê "indisponível", `disponivel` lê "disponível"
- [X] T003 Acrescentar `correspondencias` em `servidor/catalogo.py`: texto com menos de dois caracteres úteis não lista aeródromo; com dois ou mais, só aeródromo de avião da emenda vigente cujo identificador ou nome contém o texto

## Phase 3: User Story 1 - Recuperar o voo quando a conta recusa (Priority: P1)

**Goal**: A recusa devolve a mensagem e os valores informados. A confirmação de hora passada só aparece quando a hora já passou.

**Independent Test**: Enviar origem igual ao destino e ver os campos preenchidos. Enviar hora futura e não ver o pedido de hora passada. Enviar hora passada e ver o pedido.

- [X] T004 [US1] Cobrir a recusa e a hora passada em `tests/test_tela_piloto.py`
- [X] T005 [US1] Devolver os valores e o pedido de hora em `app.py` e `templates/plano_novo.html`

## Phase 4: User Story 2 - Encontrar o aeródromo digitando (Priority: P1)

**Goal**: Origem e destino não são a lista nacional. O piloto digita e vê só as correspondências.

**Independent Test**: `q=JD` devolve SBJD e não SBAU. `q=j` não devolve a lista. A página de plano novo não traz a lista nacional.

- [X] T006 [US2] Cobrir a busca em `tests/test_tela_piloto.py`
- [X] T007 [US2] Filtrar `GET /aerodromos` quando há `q` em `app.py`, e trocar as listas por campo de texto em `templates/plano_novo.html`

## Phase 5: User Story 3 - Alterar um plano e recalcular (Priority: P1)

**Goal**: O dono abre o formulário preenchido e recalcula o mesmo plano. Recusa de formulário não substitui o plano. Outro piloto é recusado.

**Independent Test**: Alterar o peso e ler o plano novo. Enviar origem igual ao destino e ver o destino antigo intacto.

- [X] T008 [US3] Cobrir alteração, recusa e piloto alheio em `tests/test_tela_piloto.py`
- [X] T009 [US3] Abrir e gravar a alteração em `app.py` e o link em `templates/plano.html`

## Phase 6: User Story 4 - Ler o estado em português (Priority: P2)

**Goal**: Painel e tela do plano usam o rótulo de planejamento. Falta de fonte lê "indisponível".

**Independent Test**: O HTML do painel contém "aceitável para planejamento". O boletim sem TAF lê "indisponível".

- [X] T010 [P] [US4] Usar `rotulo_lido` em `templates/painel.html` e `templates/plano.html`
- [X] T011 [P] [US4] Escrever "indisponível" nas linhas de boletim em `servidor/tempo.py` e no PDF em `servidor/pdf_plano.py`, e ajustar `tests/test_tempo.py`

## Phase 7: User Story 5 - Não mostrar tabela vazia (Priority: P2)

**Goal**: A tabela de grandezas só aparece quando há linha.

**Independent Test**: Plano com `linhas` vazias não mostra o cabeçalho "Grandeza"; os trechos continuam.

- [X] T012 [US5] Condicionar a tabela em `templates/plano.html` e cobrir em `tests/test_tela_piloto.py`

## Phase 8: User Story 6 - Mapa de ruas não é a carta (Priority: P2)

**Goal**: A frase fica junto do mapa. A carta se apresenta como carta de voo visual ou como indisponível.

**Independent Test**: A frase aparece antes do mapa. Sem chave de carta, a tela diz "Carta de voo visual: indisponível."

- [X] T013 [US6] Ajustar `templates/plano.html` e cobrir em `tests/test_tela_piloto.py`

## Phase 9: User Story 7 - Checklist continua visível (Priority: P2)

**Goal**: Depois de marcar, a tela reabre no item, com o estado visível.

**Independent Test**: A resposta de marcar aponta para `#item-<id>`.

- [X] T014 [US7] Ancorar o item em `templates/plano.html` e redirecionar em `app.py`, com teste em `tests/test_tela_piloto.py`

## Phase 10: Polish

- [X] T015 Rodar o pytest das telas, do boletim, do histórico e do PDF da rota

## Dependencies & Execution Order

### Phase Dependencies

- Setup não bloqueia código de produto.
- Foundational bloqueia as histórias que leem rótulo ou buscam aeródromo.
- US1 e US2 compartilham `templates/plano_novo.html` e correm em sequência.
- US3 depende do formulário da US1.
- US4, US5 e US6 mexem em `templates/plano.html` e correm em sequência.
- US7 depende da tela do plano.
- Polish fecha.

### User Story Dependencies

- US1 não depende de outra história.
- US2 pode seguir a US1 no mesmo formulário.
- US3 usa o formulário da US1.
- US4, US5, US6 e US7 são leitura da tela do plano e não mudam a conta.

### Parallel Opportunities

- T010 e T011 podem correr em paralelo.
- O restante divide os mesmos arquivos e segue em ordem.

## Parallel Example: User Story 4

```bash
Task: "Usar rotulo_lido em templates/painel.html e templates/plano.html"
Task: "Escrever indisponível em servidor/tempo.py e servidor/pdf_plano.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 e Phase 2
2. Phase 3
3. Parar e ver a recusa devolver os campos

### Incremental Delivery

1. Recusa que não esquece o voo
2. Busca de aeródromo
3. Alteração
4. Rótulos, tabela, mapa e checklist

## Notes

- Não alterar `servidor/rota.py` nem `servidor/calculo.py`.
- O estado gravado continua `calculado` ou `inaceitavel`.
- Sem dependência nova.
