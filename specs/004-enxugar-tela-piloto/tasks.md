---

description: "Task list for enxugar a tela do piloto"
---

# Tasks: Enxugar a tela do piloto

**Input**: Design documents from `/specs/004-enxugar-tela-piloto/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tela-piloto.md, quickstart.md, constitution 2.2.0

**Tests**: Incluídos em `tests/test_tela_piloto.py`. A orientação do plano e o PDF continuam cobertos por `tests/test_orientacao.py`.

**Organization**: Uma história por fase. A conta da rota, o PDF e o servidor não mudam.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode correr em paralelo (outro arquivo, sem depender de tarefa incompleta)
- **[Story]**: História da spec (US1, US2, US3)
- Cada tarefa cita o arquivo que altera

## Path Conventions

Aplicação Flask na raiz: `templates/`, `tests/`.

## Phase 1: Setup

**Purpose**: Confirmar que a feature não pede biblioteca nova

- [X] T001 Conferir que `requirements.txt` não ganha pacote: o visual fica no CSS de `templates/base.html`

## Phase 2: Foundational

**Purpose**: Visual comum das telas

- [X] T002 Em `templates/base.html`, trocar o estilo cru por página com fundo, cartão, cabeçalho, campos de uma linha, botão principal e tabela com título legível, sem biblioteca nova

## Phase 3: User Story 1 - Escolher o voo numa tela curta (Priority: P1)

**Goal**: Plano novo em Rota e Carga, com caixas de uma linha que já mostram um nome

**Independent Test**: Abrir `/planos/novo` e ver aeronave, origem e destino numa linha, os dois grupos e a frase de que não autoriza o voo

### Tests for User Story 1

- [X] T003 [US1] Em `tests/test_tela_piloto.py`, exigir caixas sem `size`, grupos Rota e Carga, e a frase "Não é autorização de voo." no plano novo

### Implementation for User Story 1

- [X] T004 [US1] Em `templates/plano_novo.html`, agrupar Rota e Carga, usar `select` de uma linha com nome real já selecionado, frase curta da lista local, frase de limite visível, e filtro só quando houver mais de doze aeródromos

**Checkpoint**: O plano novo cabe na primeira leitura e as opções continuam nas caixas

## Phase 4: User Story 2 - Ler o plano sem repetir o que já foi dito (Priority: P1)

**Goal**: Estado na frente, fonte uma vez, ausência numa linha, mapa só com rota

**Independent Test**: Abrir um plano calculado e ver a linha única de indisponível, a legenda de fontes e "Como ler este plano"

### Tests for User Story 2

- [X] T005 [US2] Em `tests/test_tela_piloto.py`, trocar a frase solta da carta indisponível pela linha única e manter a frase do mapa imediatamente antes de `#mapa`

### Implementation for User Story 2

- [X] T006 [US2] Em `templates/plano.html`, abrir pelo estado, colocar unidade no título e fontes na legenda, reunir ausências, mostrar o mapa só com dois pontos e guardar a orientação em "Como ler este plano"

**Checkpoint**: A tela do plano e o teste de orientação passam, e o PDF não muda

## Phase 5: User Story 3 - Marcar o checklist sem ruído (Priority: P2)

**Goal**: Ação, texto e fonte; "marcado" só no item marcado

**Independent Test**: Marcar um item e ver a palavra marcado nesse item, sem "não marcado" nos outros

### Tests for User Story 3

- [X] T007 [US3] Em `tests/test_tela_piloto.py`, exigir "marcado" no item marcado e a ausência de "não marcado"

### Implementation for User Story 3

- [X] T008 [US3] Em `templates/plano.html`, reescrever a linha do checklist com a ação, o texto, a fonte em segundo plano e a palavra marcado só quando o item está marcado

**Checkpoint**: O checklist volta ao item e a linha fica curta

## Phase 6: Polish

**Purpose**: Painel no mesmo visual e a suíte da tela

- [X] T009 [P] Em `templates/painel.html`, manter a lista curta dentro do visual comum, sem coluna nova
- [X] T010 Rodar `pytest tests/test_tela_piloto.py tests/test_orientacao.py tests/test_catalogo_aerodromos.py`

## Phase 7: Correção pedida pelo piloto

**Purpose**: A tela em cartão ficou pior que a primeira versão

- [X] T011 Devolver `templates/base.html`, `templates/plano_novo.html`, `templates/plano.html` e `templates/painel.html` ao visual simples da primeira tela, mantendo as caixas de seleção e o texto útil

## Phase 8: Entrada deste voo

**Purpose**: O piloto informa só tipo de avião, origem, destino, data e hora, passageiros e os dois pesos

- [X] T012 Em `servidor/calculo.py`, somar o peso das pessoas, a bagagem e o combustível de planejamento da aeronave
- [X] T013 Em `servidor/planos.py` e `app.py`, aceitar `numero_passageiros`, `peso_pessoas_kg` e `peso_bagagem_kg`, e reabrir plano antigo pela soma dos pesos de pessoas
- [X] T014 Em `templates/plano_novo.html` e `documentacao/piloto.md`, deixar só esses campos e dizer que o combustível vem do manual
- [X] T015 Atualizar `tests/conftest.py`, `tests/test_calculo.py`, `tests/test_tela_piloto.py`, os testes de rota e `suite/test_mutation_targets.py` para a nova entrada
- [X] T016 Registrar em `spec.md` e `plan.md` que tipo de avião é o modelo pequeno do RAB, origem e destino são os aeródromos de avião da emenda vigente do ROTAER, e esta feature não inventa nem carrega essas listas

## Phase 9: User Story 1 - Filtrar a caixa pelo código ou pelo nome (Priority: P1)

**Goal**: Com mais de doze aeródromos, um texto por caixa deixa só as opções em que o pedaço aparece no código ou no nome já mostrado

**Independent Test**: Abrir o plano novo com mais de doze aeródromos. Digitar um pedaço do código e um pedaço do nome, com e sem acento e sem respeitar maiúsculas. A caixa continua no lugar e só mostra esses acertos. Um texto que não está no código nem no nome não cria aeródromo. Com doze ou menos, o campo de filtro não aparece.

- [X] T017 [US1] Em `tests/test_tela_piloto.py`, cobrir o contrato de `specs/004-enxugar-tela-piloto/contracts/tela-piloto.md`: com mais de doze aeródromos cada caixa tem `data-filtra`; o texto casa parte do código ou do nome exibido, ignorando maiúsculas e acentos; texto sem esse acerto não cria opção; com doze ou menos a página não contém `data-filtra`
- [X] T018 [US1] Em `templates/plano_novo.html`, fazer o filtro de origem e destino manter a opção só quando o texto for parte do código ou do nome já mostrado, ignorando maiúsculas e acentos, sem criar opção e sem usar a cidade

## Dependencies & Execution Order

### Phase Dependencies

- Setup e visual comum vêm antes das histórias
- US1, US2 e US3 dependem do visual comum. US3 edita o mesmo `plano.html` de US2, então vem depois
- Polish fecha com o pytest
- A fase 9 depende do formulário já entregue e só altera o filtro de `templates/plano_novo.html` e o teste em `tests/test_tela_piloto.py`

### User Story Dependencies

- **US1**: `plano_novo.html`, independente do plano calculado. T018 espera T017 no mesmo fluxo do filtro
- **US2**: `plano.html`, independente do formulário
- **US3**: completa a lista no mesmo `plano.html` depois de US2

### Parallel Opportunities

- T003 pode ser escrito junto de T005 e T007 no mesmo arquivo de teste, em sequência
- T009 pode acompanhar T002

## Parallel Example: User Story 1

```bash
Task: "T003 atualizar tests/test_tela_piloto.py para a caixa de uma linha"
Task: "T004 atualizar templates/plano_novo.html"
```

## Implementation Strategy

1. Visual comum em `base.html`
2. Formulário curto
3. Plano calculado curto
4. Checklist
5. Pytest da tela, da orientação e do catálogo

## Notes

- Não editar `servidor/rota.py`, `servidor/calculo.py` nem `servidor/pdf_plano.py`
- O texto completo de orientação continua no HTML do plano e no PDF
