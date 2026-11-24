---
description: "Task list for aplicar a casca visual"
---

# Tasks: Aplicar a casca visual

**Input**: Design documents from `/specs/005-aplicar-casca-visual/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/casca-visual.md, quickstart.md, constitution 2.2.0

**Tests**: Incluídos em `tests/test_casca_visual.py` porque o plano e o quickstart nomeiam esse arquivo como a validação do contrato. Cada teste é escrito antes da tela que ele cobre e precisa falhar antes da implementação.

**Organization**: Uma história por fase. A conta, a ficha, o METAR, a carta, o radar e o checklist não mudam.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode correr em paralelo (outro arquivo, sem depender de tarefa incompleta)
- **[Story]**: História da spec (US1, US2, US3, US4)
- Cada tarefa cita o arquivo que altera

## Path Conventions

Aplicação Flask na raiz: `templates/`, `static/casca/`, `tests/`.

## Phase 1: Setup

**Purpose**: Trazer as imagens fechadas no desenho sem pacote novo

- [X] T001 Copiar a planta e o emblema do desenho fechado para `static/casca/blueprint-airport-runway.jpg` e `static/casca/emblema-plano-de-voo.png`
- [X] T002 [P] Conferir que `requirements.txt` não ganha pacote

---

## Phase 2: Foundational

**Purpose**: Classes comuns que todas as histórias usam

**⚠️ CRITICAL**: Nenhuma história começa antes desta fase

- [X] T003 Em `templates/base.html`, definir a classe do card de vidro, a classe da ampulheta e o corte de coluna em 720 px, sem biblioteca visual e sem arquivo de fonte novo

**Checkpoint**: As classes existem. As histórias podem vestir as páginas.

---

## Phase 3: User Story 1 - Reconhecer o produto em qualquer tela (Priority: P1) 🎯 MVP

**Goal**: Toda página mostra a planta da pista e o emblema Plano de Voo, e a tela estreita é uma coluna

**Independent Test**: Abrir a entrada, o cadastro, o plano novo, o plano calculado e a lista de voos, abaixo e acima de 720 px. A planta e o emblema estão visíveis. A página estreita não rola na horizontal.

### Tests for User Story 1

- [X] T004 [US1] Em `tests/test_casca_visual.py`, exigir a planta de `static/casca/` e o emblema com texto alternativo "Plano de voo" na entrada, no cadastro, no painel, no plano novo e no plano calculado

### Implementation for User Story 1

- [X] T005 [US1] Em `templates/base.html`, usar a planta como fundo de toda página e o emblema como único logo, com a coluna abaixo de 720 px sem rolagem horizontal

**Checkpoint**: A casca comum está visível em todas as páginas, sem o menu novo.

---

## Phase 4: User Story 2 - Entrar e informar o voo no mesmo vidro (Priority: P1)

**Goal**: Entrada, cadastro e plano novo usam o card central. O menu de voo não aparece antes de entrar.

**Independent Test**: Abrir a entrada e o cadastro e ver o mesmo card. Entrar e ver os sete campos, nesta ordem, sem combustível a bordo. A frase de que o resultado não autoriza o voo está visível.

### Tests for User Story 2

- [X] T006 [US2] Em `tests/test_casca_visual.py`, exigir o card de vidro na entrada e no cadastro, a ausência de "Novo voo", "Voos planejados" e "Imprimir voo" nessas duas páginas, e no plano novo os sete campos na ordem do contrato mais a frase "Não é autorização de voo."

### Implementation for User Story 2

- [X] T007 [P] [US2] Em `templates/entrar.html`, colocar identificação, senha e "Criar acesso" dentro do card de vidro
- [X] T008 [P] [US2] Em `templates/cadastro.html`, usar o mesmo card de vidro da entrada, sem o menu de voo
- [X] T009 [US2] Em `templates/plano_novo.html`, manter o card de vidro com tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem, sem combustível a bordo nem peso de piloto separado

**Checkpoint**: Dá para entrar e preencher o voo no vidro. O menu novo ainda não existe.

---

## Phase 5: User Story 3 - Esperar o cálculo sem o card (Priority: P1)

**Goal**: O envio esconde o card e mostra "Em processamento" até a resposta

**Independent Test**: Enviar um plano válido e ver a ampulheta no lugar do card. Enviar um plano recusado e ver o card de volta com os valores.

### Tests for User Story 3

- [X] T010 [US3] Em `tests/test_casca_visual.py`, exigir em `templates/plano_novo.html` a frase "Em processamento", a ampulheta, e que o script do envio não calcule distância, combustível, vento, carta nem PDF

### Implementation for User Story 3

- [X] T011 [US3] Em `templates/plano_novo.html`, no envio do plano novo e da alteração, esconder o card, mostrar a ampulheta com "Em processamento" e impedir o menu de abrir outra tela até a resposta. A espera é estado da página, não do banco.

**Checkpoint**: A espera do cálculo está visível. O resumo e o menu ainda não.

---

## Phase 6: User Story 4 - Manter o resumo e o menu (Priority: P2)

**Goal**: O resumo fica acima dos trechos e o menu autenticado oferece Novo voo, Voos planejados, Imprimir voo e Sair

**Independent Test**: Abrir um plano com dois trechos, trocar a aba e ver o mesmo resumo. Usar cada item do menu. Sem plano aberto, Imprimir voo mostra "Não há voo para imprimir." e a tela permanece.

### Tests for User Story 4

- [X] T012 [US4] Em `tests/test_casca_visual.py`, exigir o menu só com sessão, "Sair" como envio e não como link de leitura, "Não há voo para imprimir." fora de um plano aberto, o PDF no plano aberto, e o resumo acima dos trechos sem técnica de decolagem nem de pouso

### Implementation for User Story 4

- [X] T013 [P] [US4] Em `templates/base.html`, mostrar o menu só quando a sessão tem piloto, com Novo voo, Voos planejados, Imprimir voo e Sair. A entrada e o cadastro não têm esse menu. Sem plano aberto, Imprimir voo revela "Não há voo para imprimir." na mesma página. Sair continua o envio que encerra a sessão.
- [X] T014 [P] [US4] Em `templates/plano.html`, colocar acima dos trechos o resumo com o código de saída, o de chegada e os números já calculados de cada trecho, e apontar Imprimir voo para o PDF desse plano. O resumo não é tabela nova e não muda ao trocar a aba.

**Checkpoint**: As quatro histórias funcionam. A conta e o miolo da ficha continuam os da especificação 004.

---

## Phase 7: Polish

**Purpose**: Conferir que a casca não apaga o que a 004 já exige

- [X] T015 Seguir `specs/005-aplicar-casca-visual/quickstart.md` e rodar `pytest tests/test_casca_visual.py tests/test_tela_piloto.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: começa agora
- **Foundational (Phase 2)**: depende do Setup e bloqueia as histórias
- **Histórias (Phase 3+)**: dependem da Phase 2. US2 e US3 usam o card da Phase 2. US4 usa a página já vestida.
- **Polish**: depende das histórias que forem entregues

### User Story Dependencies

- **US1**: depois da Phase 2. Não depende das outras histórias.
- **US2**: depois da Phase 2. Usa o card da Phase 2 e não precisa do menu.
- **US3**: depois da US2, porque a ampulheta esconde o card do plano novo.
- **US4**: depois da US1, porque o menu mora no mesmo `templates/base.html`. O resumo em `templates/plano.html` não depende da ampulheta.

### Within Each User Story

- O teste da história fica antes da implementação e deve falhar antes dela
- T007 e T008 podem correr juntos, depois de T006
- T013 e T014 podem correr juntos, depois de T012

### Parallel Opportunities

- T001 e T002 em arquivos diferentes
- T007 e T008 em `templates/entrar.html` e `templates/cadastro.html`
- T013 e T014 em `templates/base.html` e `templates/plano.html`

---

## Parallel Example: User Story 2

```bash
# Depois de T006:
Task: "Em templates/entrar.html, colocar identificação, senha e Criar acesso no card de vidro"
Task: "Em templates/cadastro.html, usar o mesmo card de vidro da entrada"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Terminar Phase 1 e Phase 2
2. Terminar a User Story 1
3. Parar e abrir as cinco páginas. A planta e o emblema bastam para o primeiro incremento.

### Incremental Delivery

1. Setup e fundação
2. US1: a casca comum
3. US2: entrada e plano novo no vidro
4. US3: a espera do cálculo
5. US4: resumo e menu
6. Polish com o pytest do quickstart

### Parallel Team Strategy

1. Todos terminam Setup e Foundational
2. Uma pessoa segue US1 e depois o menu em `templates/base.html`
3. Outra segue US2 e US3 em `templates/entrar.html`, `templates/cadastro.html` e `templates/plano_novo.html`
4. O resumo em `templates/plano.html` pode acompanhar o menu

---

## Notes

- [P] só quando o arquivo é outro e a tarefa anterior da história já terminou
- A espera não grava campo. O resumo não cria tabela.
- Não alterar `servidor/` nem `app.py` para esta casca
- Commitar depois de cada tarefa ou de cada história
