---

description: "Task list for rota com escalas"
---

# Tasks: Rota com escalas

**Input**: Design documents from `/specs/002-rota-com-escalas/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-rota.md, quickstart.md, constitution 3.0.0

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

## Phase 4: User Story 2 - Escolher um avião pequeno com dados técnicos completos (Priority: P1)

**Goal**: A lista são os aviões pequenos do extrato, em frota decrescente; modelo sem dados técnicos completos não calcula

**Independent Test**: O modelo sem fonte técnica aplicável é recusado. O modelo completo calcula com a fonte registrada. Avião acima de 5.670 kg não entra.

- [X] T008 [P] [US2] Escrever em `tests/test_catalogo_aeronaves.py` os testes que falham: ordem pela frota, recusa do modelo sem manual, exclusão do avião grande
- [X] T009 [US2] Implementar a leitura do extrato público do RAB em `servidor/catalogo.py`, sem copiar número de um manual para outro modelo
- [X] T010 [US2] Ligar `GET /aeronaves` em `app.py` e impedir em `servidor/planos.py` o cálculo quando `manual_estado` é `ausente`

**Checkpoint**: O teste de US2 passa. Valores já registrados permanecem armazenados, mas só dados com fonte aplicável e verificável podem ser usados.

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
- [X] T017 [US4] Acrescentar em `documentacao/piloto.md` o que é uma escala, o que significa catálogo indisponível e o que significa modelo sem dados técnicos completos, sem segunda cópia desse texto no código

**Checkpoint**: A tela e o PDF usam o texto de `documentacao/piloto.md`.

---

## Phase 7: Polish

- [X] T018 Rodar `tests/` e corrigir falha que una o plano direto com a rota, sem mudar a reserva de 30 minutos nem o isolamento
- [X] T019 Percorrer `specs/002-rota-com-escalas/quickstart.md` e anotar no fim de `documentacao/operacao.md` só o comando real de carga, sem chave e sem número de manual
- [X] T020 Confirmar que `templates/` não ganhou fórmula de distância nem número novo de manual

---

## Phase 8: User Story 2 - Oferecer somente modelos completos do MVP (Priority: P1)

**Goal**: A lista contém no máximo os 30 primeiros modelos completos, com fonte oficial ou secundária rastreável, pela frota RAB vigente; valores secundários são estimativas didáticas. Sem RAB atual, a lista fica indisponível e vazia. Modelos fora da lista não calculam.

**Independent Test**: Com RAB e fontes fictícias, a seleção exige procedência por campo, aplica a regra de fonte mais recente, filtra completude antes de ordenar e cortar em 30 e rotula dados secundários como estimativas didáticas; sem RAB retorna lista vazia. `POST` e `PUT` recusam modelos incompletos ou fora do limite.

### Tests for User Story 2

> Escrever os testes primeiro e confirmar que falham antes da implementação.

- [X] T021 [US2] Adicionar em `tests/test_catalogo_aeronaves.py`, `tests/test_rota.py` e `tests/test_tela_piloto.py` testes para completude antes do corte, limite 30, empate por nome, associação exata, registro legado sem fonte técnica rastreável inelegível, RAB indisponível sem fallback, recusa em `POST`/`PUT` e mensagem de lista vazia

### Implementation for User Story 2

- [X] T022 [US2] Remover a associação aproximada e implementar completude, ordenação e limite de 30 após o filtro em `servidor/catalogo.py`; sem extrato vigente, retornar `indisponivel` e lista vazia
- [X] T023 [US2] Validar em `servidor/planos.py` que o modelo pertence à seleção elegível vigente tanto na criação quanto na alteração do plano
- [X] T024 [US2] Propagar o estado do RAB em `app.py` e mostrar em `templates/plano_novo.html` a indisponibilidade ou ausência de modelos elegíveis, sem permitir envio quando a lista estiver vazia
- [X] T025 [P] [US2] Alterar `servidor/semente.py` e criar migração de dados em `alembic/versions/` para aplicar `ausente` a qualquer registro legado sem fonte técnica rastreável e aplicável, preservando os valores existentes e impedindo seu uso em cálculos, sem condição por nome de modelo
- [ ] T026 [US2] Obter o extrato público vigente do RAB, confirmar a unidade de `NR_PMD` no dicionário oficial antes de aplicar o limite de 5.670 kg, configurar `RAB_EXTRATO` para arquivo externo identificado por publicação/data e registrar a referência em `servidor/catalogo.py` sem versionar o arquivo bruto
- [ ] T027 [US2] Pesquisar fontes oficiais e secundárias dos candidatos em ordem de frota, registrar em `specs/002-rota-com-escalas/research.md` publicador, referência, data e aplicabilidade por campo, e distinguir dados confirmados de lacunas
- [X] T028 [P] [US2] Atualizar `documentacao/piloto.md` e `documentacao/operacao.md` para explicar o limite de 30, os modelos em espera, o comportamento sem RAB vigente e como configurar `RAB_EXTRATO` sem expor chave ou extrato bruto
- [ ] T029 [P] [US2] Adicionar em `tests/test_catalogo_aeronaves.py` e `tests/test_migracao_aeronaves.py` testes para procedência obrigatória por campo, fonte mais recente, empate sem seleção, registro de conflito e inelegibilidade de dados sem data ou aplicabilidade. **Parcial**: `test_fonte_mais_recente_e_empate_sem_selecao` cobre recência, empate e divergência; falta provar inelegibilidade sem data/aplicabilidade.
- [X] T030 [US2] Criar `FonteTecnicaAeronave` em `servidor/modelos.py` e migração Alembic em `alembic/versions/`; exigir fonte, publicador, referência, datas verificáveis, aplicabilidade e perfil de cruzeiro, com no máximo uma fonte selecionada por aeronave/campo. **Verificado**: modelo, migração e validação estão presentes; suíte completa passou.
- [X] T031 [US2] Implementar em `servidor/catalogo.py` a validação de completude com proveniência por campo e a seleção da fonte aplicável mais recente, preservando conflitos e sem fazer média. **Verificado**: `servidor/proveniencia.py` implementa seleção temporal e empate sem seleção; suíte completa passou.
- [ ] T032 [US2] Registrar em `servidor/semente.py` até 30 modelos completos em ordem RAB, com fonte e data verificáveis para cada campo; usar dados secundários somente como estimativas didáticas e deixar lacunas indisponíveis
- [ ] T033 [P] [US4] Adicionar em `tests/test_tela_piloto.py`, `tests/test_rota_pdf.py` e `tests/test_catalogo_aeronaves.py` testes para exibição de publicador, referência, data, aplicabilidade e rótulo didático na seleção, resultado e PDF. **Parcial/supersedido**: a seleção agora mostra somente o nome (007/T019); faltam testes de metadados factuais no resultado/PDF.
- [X] T034 [US4] Expor procedência por campo e `estimativa_didatica` em `app.py` e mostrar fonte e rótulo na seleção em `templates/plano_novo.html`. **Ajustado por 007/T019**: a API expõe a procedência; a seleção mostra somente o nome por decisão posterior, com detalhes no resultado/PDF.
- [X] T035 [US4] Propagar fonte dos valores de entrada e o estado de estimativa em `servidor/calculo.py`, `servidor/rota.py`, `templates/plano.html` e `servidor/pdf_plano.py`. **Verificado**: as fontes são propagadas pelo cálculo e exibidas no resultado/PDF; testes focados e suíte completa passaram.
- [ ] T036 [US4] Atualizar `documentacao/piloto.md` e `documentacao/operacao.md` com fontes secundárias, estimativas didáticas, conflitos e dados indisponíveis

---

## Phase 9: Polish

**Purpose**: Confirmar a regressão e os cenários executáveis da atualização de catálogo.

- [ ] T037 Executar `pytest` e seguir `specs/002-rota-com-escalas/quickstart.md`, verificando RAB vigente e indisponível, procedência por campo, fonte conflitante, rótulos didáticos e modelos incompletos sem preenchimento. **Parcial**: `pytest` completo passou (136 testes); validação do RAB vigente e cenários externos do quickstart não foi executada.
- [X] T038 [US1/US3] Adicionar teste de regressão para manter a lista local identificada para consulta e seleção, mas recusar criação e cálculo de plano sem emenda ROTAER vigente em `servidor/planos.py` e `tests/test_rota.py`

---

## Dependencies & Execution Order

- Phase 1 e Phase 2 bloqueiam as histórias
- US1 e US2 podem seguir em paralelo depois da Phase 2
- US3 depende de US1 e US2
- US4 depende de US3
- Phase 7 fecha
- Phase 8 reabre somente US2 para completar a regra do MVP e depende das fases anteriores já concluídas
- T022 depende de T021; T023 depende de T022; T024 depende de T022
- T025 e T028 podem correr em paralelo com T022 após T021
- T027 depende de T026; T029 pode correr em paralelo com T026 e T027
- T030 depende de T029; T031 depende de T030
- T032 depende de T026, T027 e T031
- T033 depende de T029 e pode correr em paralelo com T030–T032; T034 depende de T033 e T031; T035 depende de T034
- T036 depende de T034 e T035; T037 depende de todas as tarefas pendentes da Phase 8

### Parallel Example: catálogos

```bash
# Arquivos de teste diferentes, depois da migração:
# tests/test_catalogo_aerodromos.py
# tests/test_catalogo_aeronaves.py
```

### Parallel Example: atualização do catálogo MVP

```bash
# Após T021, trabalhos em arquivos independentes:
servidor/catalogo.py
servidor/semente.py e alembic/versions/
documentacao/piloto.md e documentacao/operacao.md
```

## Implementation Strategy

1. T001–T020 continuam concluídas e não devem ser reabertas sem evidência de regressão.
2. T021 cria os testes que falham para a seleção atual.
3. T022–T024 implementam a seleção estrita e o bloqueio no servidor e na tela.
4. T025–T032 preservam a inelegibilidade de registros sem fonte verificável, obtêm RAB e fontes por campo e carregam somente modelos completos; se houver menos de 30, oferecer menos.
5. T033–T036 cobrem rótulo de estimativa, fontes por grandeza e documentação; T037 valida a suíte e o quickstart.

## Notes

- Não reabra fórmula no JavaScript
- Não copie número de manual para HTML, teste ou segundo modelo
- Chave e extrato com dado sensível ficam fora do repositório
- A semente de sete indicativos não substitui a emenda vigente
- T026 e T027 aguardam extrato RAB vigente e fontes técnicas aplicáveis com data verificável. Não inventar dados, combinar valores conflitantes nem tornar a seleção local um fallback.
