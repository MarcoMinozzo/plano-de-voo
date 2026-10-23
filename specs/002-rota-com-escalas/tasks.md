---

description: "Task list for rota com escalas"
---

# Tasks: Rota com escalas

**Input**: Design documents from `/specs/002-rota-com-escalas/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-rota.md, quickstart.md, constitution 2.2.0

**Tests**: Incluídos. Escrever o teste antes e vê-lo falhar. A publicação usada no teste é pequena e fictícia. A carga nacional real não roda dentro do pytest.

**Organization**: Catálogo de aeródromos, catálogo de aviões, rota, depois a tela e o PDF. A rota depende dos dois catálogos.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode correr em paralelo (outro arquivo, sem depender de tarefa incompleta)
- **[Story]**: História da spec (US1…US4)
- Cada tarefa cita o arquivo que altera

## Path Conventions

Aplicação Flask na raiz: `servidor/`, `templates/`, `tests/`, `alembic/`, `documentacao/`.

## Phase 1: Setup

**Purpose**: Confirmar que a feature não pede biblioteca nova

- [ ] T001 Conferir `requirements.txt` e não acrescentar pacote: a carga do ROTAER e do RAB usa o `requests` 2.31.0 já fixado

---

## Phase 2: Foundational

**Purpose**: O banco aceita emenda, tipo de lugar, frota e trecho. Bloqueia as histórias.

- [ ] T002 Estender `servidor/modelos.py` com EmendaRotaer, tipo do aeródromo, ExtratoRab, frota e estado do manual no modelo de avião, e Trecho ligado ao plano com apagamento em cascata
- [ ] T003 Gerar a migração Alembic em `alembic/versions/` a partir desses campos
- [ ] T004 [P] Criar `tests/conftest_rota.py` com uma emenda de três aeródromos de avião, um heliponto, dois modelos com manual e um modelo sem manual

**Checkpoint**: A migração aplica. O teste ainda não chama a rota.

---

## Phase 3: User Story 1 - Usar qualquer aeródromo brasileiro (Priority: P1)

**Goal**: A lista oferecida é a dos aeródromos de avião da emenda vigente

**Independent Test**: Um aeródromo da emenda fictícia que não é dos sete antigos serve de origem. O heliponto não serve. Sem emenda disponível, a resposta é catálogo indisponível.

- [ ] T005 [P] [US1] Escrever em `tests/test_catalogo_aerodromos.py` os testes que falham: lista só aeródromo, rejeita heliponto, e emenda ausente devolve `indisponivel` sem coordenada nova
- [ ] T006 [US1] Implementar a leitura da área `rotaer` em `servidor/catalogo.py`, gravando só a emenda vigente e marcando `indisponivel` sem chave, sem corpo ou sem emenda
- [ ] T007 [US1] Ligar `GET /aerodromos` em `app.py`, oferecendo apenas tipo `aerodromo` da emenda disponível

**Checkpoint**: O teste de US1 passa sem a rota pronta.

---

## Phase 4: User Story 2 - Escolher um avião pequeno com manual (Priority: P1)

**Goal**: A lista são os aviões pequenos do extrato, frota decrescente, e sem manual não calcula

**Independent Test**: O modelo sem manual é recusado pelo nome. O modelo com manual calcula com a fonte do manual. Avião acima de 5.670 kg não entra.

- [ ] T008 [P] [US2] Escrever em `tests/test_catalogo_aeronaves.py` os testes que falham: ordem pela frota, recusa do modelo sem manual, exclusão do avião grande
- [ ] T009 [US2] Implementar a leitura do extrato público do RAB em `servidor/catalogo.py`, sem copiar número de um manual para outro modelo
- [ ] T010 [US2] Ligar `GET /aeronaves` em `app.py` e impedir em `servidor/planos.py` o cálculo quando `manual_estado` é `ausente`

**Checkpoint**: O teste de US2 passa. O Cessna 140 já gravado continua com os mesmos números.

---

## Phase 5: User Story 3 - Receber a melhor rota e as escalas (Priority: P1)

**Goal**: O servidor escolhe o direto ou as escalas, pelo menor tempo

**Independent Test**: Direto que cabe volta um trecho. Direto que não cabe na reserva de 30 minutos volta escala com cada trecho dentro da regra, ou plano inaceitável com motivo. Nenhuma escala sai do catálogo.

- [ ] T011 [P] [US3] Escrever em `tests/test_rota.py` os testes que falham: direto único, escala quando o combustível mais 30 minutos não cobre, empate resolvido por menos escalas e depois por distância, vento ausente sem crédito de cauda, rota impossível gravada como `inaceitavel`
- [ ] T012 [US3] Implementar a escolha em `servidor/rota.py`, chamando `servidor/calculo.py` por trecho e ligando só pares que cabem no alcance de planejamento
- [ ] T013 [US3] Gravar os trechos em `servidor/planos.py` no `POST /planos` e no `PUT /planos/{id}`, sem campo de escala na entrada

**Checkpoint**: O teste de US3 passa com a emenda fictícia.

---

## Phase 6: User Story 4 - Ler a rota na tela e no PDF (Priority: P2)

**Goal**: Tela e PDF mostram os trechos, a hipótese de reabastecimento e o aviso

**Independent Test**: O PDF contém a ordem dos trechos, a frase de reabastecimento até o combustível de planejamento e "não autoriza o voo". O JavaScript não calcula distância.

- [ ] T014 [P] [US4] Escrever em `tests/test_rota_pdf.py` o teste que falha se o PDF ou o HTML omitir trecho, hipótese de reabastecimento ou o aviso
- [ ] T015 [US4] Mostrar os trechos em `templates/plano.html` e desenhar no Leaflet só os pontos já calculados
- [ ] T016 [US4] Imprimir os trechos em `servidor/pdf_plano.py`
- [ ] T017 [US4] Acrescentar em `documentacao/piloto.md` o que é uma escala, o que significa catálogo indisponível e o que significa modelo sem manual, sem segunda cópia desse texto no código

**Checkpoint**: A tela e o PDF usam o texto de `documentacao/piloto.md`.

---

## Phase 7: Polish

- [ ] T018 Rodar `tests/` e corrigir falha que una o plano direto com a rota, sem mudar a reserva de 30 minutos nem o isolamento
- [ ] T019 Percorrer `specs/002-rota-com-escalas/quickstart.md` e anotar no fim de `documentacao/operacao.md` só o comando real de carga, sem chave e sem número de manual
- [ ] T020 Confirmar que `templates/` não ganhou fórmula de distância nem número novo de manual

---

## Dependencies & Execution Order

- Phase 1 e Phase 2 bloqueiam as histórias
- US1 e US2 podem seguir em paralelo depois da Phase 2
- US3 depende de US1 e US2
- US4 depende de US3
- Phase 7 fecha

### Parallel Example: catálogos

```bash
# Arquivos de teste diferentes, depois da migração:
# tests/test_catalogo_aerodromos.py
# tests/test_catalogo_aeronaves.py
```

## Implementation Strategy

1. Phase 2 deixa o banco pronto
2. US1 e US2 provam o catálogo sem otimizar rota
3. US3 entrega a rota
4. US4 mostra e imprime

## Notes

- Não reabra fórmula no JavaScript
- Não copie número de manual para HTML, teste ou segundo modelo
- Chave e extrato com dado sensível ficam fora do repositório
- A semente de sete indicativos não substitui a emenda vigente
