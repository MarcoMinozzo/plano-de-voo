# Tasks: Apresentação legível de METAR e TAF

**Input**: Design documents from `specs/032-metar-taf-display/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/meteorologia-ui.md`

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

Nenhuma tarefa de setup: aplicação, dependências e estrutura já existem.

## Phase 2: Foundational

**Purpose**: Blocking prerequisites for user stories

Nenhuma tarefa fundacional: a leitura é derivada em memória e não exige migração.

## Phase 3: User Story 1 - Ler METAR e TAF em formato organizado (Priority: P1)

**Goal**: Preservar os textos originais e apresentar leituras organizadas de METAR e dos grupos TAF na ficha do trecho.

**Independent Test**: Simular um METAR estruturado e um TAF com grupos base, FM, BECMG, TEMPO e PROB; confirmar campos, períodos e textos originais na página.

### Tests for User Story 1

- [X] T001 [P] [US1] Adicionar testes em `tests/test_tempo.py` para interpretação dos campos METAR e dos grupos/períodos TAF, confirmando que a string original não é modificada.
- [X] T002 [P] [US1] Adicionar testes em `tests/test_tela_piloto.py` para confirmar blocos originais estilo terminal, tabelas METAR/TAF e preservação do estado indisponível.

### Implementation for User Story 1

- [X] T003 [US1] Implementar `campos_taf` em `servidor/tempo.py`, separando grupos base, FM, BECMG, TEMPO e PROB e extraindo campos sem misturar períodos.
- [X] T004 [US1] Enriquecer `app.py::_boletins_por_aerodromo` com a leitura TAF calculada no servidor, sem alterar ou persistir o boletim original.
- [X] T005 [US1] Atualizar a apresentação meteorológica em `templates/plano.html` para blocos monoespaçados escuros e tabelas de leitura com contêiner responsivo.

**Checkpoint**: Cada METAR/TAF disponível mantém sua string original e mostra uma leitura tabular coerente; boletins indisponíveis continuam explícitos.

## Phase 4: User Story 2 - Entender os códigos de fenômenos meteorológicos (Priority: P2)

**Goal**: Mostrar explicações internas em português para fenômenos conhecidos em METAR e TAF, mantendo códigos desconhecidos visíveis.

**Independent Test**: Verificar tradução de intensidade, descritor e precipitação combinados e confirmar que um código desconhecido aparece como não interpretado.

### Tests for User Story 2

- [X] T006 [US2] Adicionar testes em `tests/test_tempo.py` para explicações conhecidas, composição de códigos e preservação de códigos desconhecidos sem tradução inventada.

### Implementation for User Story 2

- [X] T007 [US2] Implementar o catálogo interno e a interpretação de fenômenos em `servidor/tempo.py`, aplicando o resultado aos campos METAR e aos grupos TAF.
- [X] T008 [US2] Exibir código e explicação na leitura tabular METAR/TAF em `templates/plano.html`, marcando componentes desconhecidos como não interpretados.

**Checkpoint**: Fenômenos reconhecidos têm explicação em português; tokens não reconhecidos continuam visíveis sem descrição aproximada.

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T009 Executar os testes de `specs/032-metar-taf-display/quickstart.md`, compilar `static/css/tailwind.css` a partir de `static/css/input.css` e verificar `git diff --check`.
- [X] T010 Conferir o layout da página em viewport móvel de 390 px conforme `specs/032-metar-taf-display/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup**: sem tarefas; estrutura existente.
- **Foundational**: sem tarefas; sem migração ou infraestrutura nova.
- **User Story 1**: independente após a especificação e o contrato.
- **User Story 2**: depende da estrutura dos grupos TAF de US1 para explicar fenômenos dentro de cada período.
- **Polish**: depende das duas histórias.

### User Story Dependencies

- **US1 (P1)**: pode ser implementada e validada sozinha; é o MVP.
- **US2 (P2)**: amplia a leitura apresentada por US1; requer a estrutura de campos METAR/TAF disponível.

### Within Stories

- T001 e T002 podem ser preparados em paralelo, pois alteram arquivos de teste distintos.
- T003 precede T004 e T005; os consumidores dependem da estrutura de grupos.
- T006 deve falhar antes de T007 implementar a tradução.
- T007 precede T008; a interface apenas apresenta explicações já calculadas.
- T009 e T010 executam após as duas histórias.

## Parallel Example: User Story 1

```text
Task: T001 — parser e períodos METAR/TAF em tests/test_tempo.py
Task: T002 — blocos e tabelas da ficha em tests/test_tela_piloto.py
```

## Implementation Strategy

1. Entregar US1 como MVP: parser no servidor, preparação do view-model e apresentação responsiva.
2. Entregar US2 acrescentando tradução determinística ao mesmo view-model.
3. Preservar o texto original em todas as etapas; a leitura tabular nunca o substitui.
4. Executar os testes focados, compilar o CSS e conferir visualmente a largura móvel.

## Notes

- [P] identifica apenas tarefas em arquivos distintos sem dependências incompletas.
- O parser não consulta APIs nem grava a interpretação no plano.
- Não alterar a geração do PDF ou as consultas meteorológicas nesta feature.
