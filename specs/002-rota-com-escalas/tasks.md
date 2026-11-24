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

- [X] T001 Conferir `requirements.txt` e não acrescentar pacote: a carga do ROTAER e do RAB usa o `requests` 2.31.0 já fixado

---

## Phase 2: Foundational

**Purpose**: O banco aceita emenda, tipo de lugar, frota e trecho. Bloqueia as histórias.

- [X] T002 Estender `servidor/modelos.py` com EmendaRotaer, tipo do aeródromo, ExtratoRab, frota e estado do manual no modelo de avião, e Trecho ligado ao plano com apagamento em cascata
- [X] T003 Gerar a migração Alembic em `alembic/versions/` a partir desses campos
- [X] T004 [P] Criar `tests/conftest_rota.py` com uma emenda de três aeródromos de avião, um heliponto, dois modelos com manual e um modelo sem manual

**Checkpoint**: A migração aplica. O teste ainda não chama a rota.

---

## Phase 3: User Story 1 - Usar qualquer aeródromo brasileiro (Priority: P1)

**Goal**: A lista oferecida é a dos aeródromos de avião da emenda vigente

**Independent Test**: Um aeródromo da emenda fictícia que não é dos sete antigos serve de origem. O heliponto não serve. Sem emenda disponível, a resposta é catálogo indisponível.

- [X] T005 [P] [US1] Escrever em `tests/test_catalogo_aerodromos.py` os testes que falham: lista só aeródromo, rejeita heliponto, e emenda ausente devolve `indisponivel` sem coordenada nova
- [X] T006 [US1] Implementar a leitura da área `rotaer` em `servidor/catalogo.py`, gravando só a emenda vigente e marcando `indisponivel` sem chave, sem corpo ou sem emenda
- [X] T007 [US1] Ligar `GET /aerodromos` em `app.py`, oferecendo apenas tipo `aerodromo` da emenda disponível

**Checkpoint**: O teste de US1 passa sem a rota pronta.

---

## Phase 4: User Story 2 - Escolher um avião pequeno com manual (Priority: P1)

**Goal**: A lista são os aviões pequenos do extrato, frota decrescente, e sem manual não calcula

**Independent Test**: O modelo sem manual é recusado pelo nome. O modelo com manual calcula com a fonte do manual. Avião acima de 5.670 kg não entra.

- [X] T008 [P] [US2] Escrever em `tests/test_catalogo_aeronaves.py` os testes que falham: ordem pela frota, recusa do modelo sem manual, exclusão do avião grande
- [X] T009 [US2] Implementar a leitura do extrato público do RAB em `servidor/catalogo.py`, sem copiar número de um manual para outro modelo
- [X] T010 [US2] Ligar `GET /aeronaves` em `app.py` e impedir em `servidor/planos.py` o cálculo quando `manual_estado` é `ausente`

**Checkpoint**: O teste de US2 passa. O Cessna 140 já gravado continua com os mesmos números.

---

## Phase 5: User Story 3 - Receber a melhor rota e as escalas (Priority: P1)

**Goal**: O servidor escolhe o direto ou as escalas, pelo menor tempo

**Independent Test**: Direto que cabe volta um trecho. Direto que não cabe na reserva de 30 minutos volta escala com cada trecho dentro da regra, ou plano inaceitável com motivo. Nenhuma escala sai do catálogo.

- [X] T011 [P] [US3] Escrever em `tests/test_rota.py` os testes que falham: direto único, escala quando o combustível mais 30 minutos não cobre, empate resolvido por menos escalas e depois por distância, vento ausente sem crédito de cauda, rota impossível gravada como `inaceitavel`
- [X] T012 [US3] Implementar a escolha em `servidor/rota.py`, chamando `servidor/calculo.py` por trecho e ligando só pares que cabem no alcance de planejamento
- [X] T013 [US3] Gravar os trechos em `servidor/planos.py` no `POST /planos` e no `PUT /planos/{id}`, sem campo de escala na entrada

**Checkpoint**: O teste de US3 passa com a emenda fictícia.

---

## Phase 6: User Story 4 - Ler a rota na tela e no PDF (Priority: P2)

**Goal**: Tela e PDF mostram os trechos, a hipótese de reabastecimento e o aviso

**Independent Test**: O PDF contém a ordem dos trechos, a frase de reabastecimento até o combustível de planejamento e "não autoriza o voo". O JavaScript não calcula distância.

- [X] T014 [P] [US4] Escrever em `tests/test_rota_pdf.py` o teste que falha se o PDF ou o HTML omitir trecho, hipótese de reabastecimento ou o aviso
- [X] T015 [US4] Mostrar os trechos em `templates/plano.html` e desenhar no Leaflet só os pontos já calculados
- [X] T016 [US4] Imprimir os trechos em `servidor/pdf_plano.py`
- [X] T017 [US4] Acrescentar em `documentacao/piloto.md` o que é uma escala, o que significa catálogo indisponível e o que significa modelo sem manual, sem segunda cópia desse texto no código

**Checkpoint**: A tela e o PDF usam o texto de `documentacao/piloto.md`.

---

## Phase 7: Polish

- [X] T018 Rodar `tests/` e corrigir falha que una o plano direto com a rota, sem mudar a reserva de 30 minutos nem o isolamento
- [X] T019 Percorrer `specs/002-rota-com-escalas/quickstart.md` e anotar no fim de `documentacao/operacao.md` só o comando real de carga, sem chave e sem número de manual
- [X] T020 Confirmar que `templates/` não ganhou fórmula de distância nem número novo de manual

---

## Phase 8: Manuais dos 20 modelos — clarificação de 2026-11-24 (US2)

**Goal**: Os 20 modelos não experimentais de maior frota calculam o plano com números do manual oficial, cada um com documento e página.

**Independent Test**: Depois de `python -m servidor.manuais`, um modelo da tabela de [research.md](./research.md#os-20-modelos) calcula o plano, e a fonte cita documento e página. O RV-10 continua recusado pelo nome. O Cessna 140 calcula como antes.

### Fundação

- [X] T021 Acrescentar `combustivel_kg_por_gal` (Float, opcional) ao modelo `Aeronave` em `servidor/modelos.py`
- [X] T022 Gerar em `alembic/versions/` a migração da coluna `combustivel_kg_por_gal`, com `downgrade` que a remove

### Testes (escrever antes e ver falhar)

- [X] T023 [P] [US2] Escrever `tests/test_manuais.py` com arquivos fictícios em `tmp_path`: arquivo válido grava `gravado` com fonte de documento e página; lb, in, L, mph, km/h, L/h e lb/h viram kg, m, gal, kt e gal/h; campo, unidade ou página faltando recusa pelo nome do campo; `experimental` verdadeiro recusa; máximo acima de 5.670 kg ou vazio igual ou maior que o máximo recusa; rodar duas vezes dá o mesmo banco; o Cessna 140 não muda; `carregar_rab` depois da carga mantém o modelo `gravado`
- [X] T024 [P] [US2] Acrescentar em `tests/test_calculo.py` que o peso do combustível usa `combustivel_kg_por_gal` do modelo e, sem ele, os 2,72 kg/gal de avgas

### Implementação

- [X] T025 [US2] Criar `servidor/manuais.py` conforme `contracts/registro-manual.md`: ler `servidor/manuais/*.json`, validar, converter com os fatores exatos de `research.md`, compor `fonte_manual` com documento, páginas e condição de cruzeiro, gravar pelo nome do RAB e imprimir `gravado:` ou `recusado:`, com código de saída 0 ou 1
- [X] T026 [US2] Em `servidor/calculo.py`, usar `combustivel_kg_por_gal` do modelo em `avaliar_carga`, com `KG_POR_GAL` como padrão, e citar a fonte do manual na linha do peso
- [ ] T027 [US2] Transcrever em `servidor/manuais/` os modelos 1 a 10 da tabela de `research.md`, de manual oficial com cópia pública, com a página de cada número. Modelo sem cópia pública fica sem arquivo, e o próximo não experimental da frota entra; registrar a troca no PR. Um PR só para este lote, revisado número por número pelo piloto responsável
- [ ] T028 [US2] Transcrever em `servidor/manuais/` os modelos 11 a 20 da mesma tabela, com a mesma regra e um PR só para este lote

### Fechamento

- [X] T029 Acrescentar `python -m servidor.manuais` à carga em `documentacao/operacao.md`, depois de `python -m servidor.catalogo`, sem número de manual
- [X] T030 Rodar `pytest tests/test_manuais.py tests/test_calculo.py tests/test_catalogo_aeronaves.py tests/test_rota.py tests/review/test_module_shape.py` e corrigir falha
- [ ] T031 Percorrer os passos 4 e 5 de `quickstart.md` com o extrato do RAB do piloto responsável e anotar no PR quantos modelos ficaram `gravado`

**Checkpoint**: T021 a T026 entregam a carga sem nenhum manual real. T027 e T028 trazem os números, e cada lote pode entrar sozinho.

---

## Dependencies & Execution Order

- Phase 1 e Phase 2 bloqueiam as histórias
- US1 e US2 podem seguir em paralelo depois da Phase 2
- US3 depende de US1 e US2
- US4 depende de US3
- Phase 7 fecha
- Phase 8: T021 e T022 antes de tudo; T023 e T024 em paralelo; T025 e T026 depois dos testes; T027 e T028 depois de T025 e independentes entre si; T029 a T031 fecham

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
