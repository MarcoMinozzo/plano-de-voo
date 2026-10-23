---

description: "Task list for planejar voo visual"
---

# Tasks: Planejar voo visual

As tarefas do catálogo nacional e da rota com escalas estão em `specs/002-rota-com-escalas/tasks.md`. As tarefas abaixo permanecem as do plano direto.

**Input**: Design documents from `/specs/001-planejar-voo-visual/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-plano.md, quickstart.md, constitution 2.1.1

**Tests**: Incluídos. O plano e a constituição 2.1.1 pedem pytest para cálculo, limite do manual, isolamento, senha curta, bloqueio e sessão encerrada. Escrever o teste antes e vê-lo falhar.

**Organization**: Uma fase por história. US1 se prova com um piloto criado no teste. US2 é a porta real de entrada.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode correr em paralelo (outro arquivo, sem depender de tarefa incompleta)
- **[Story]**: História da spec (US1…US7)
- Cada tarefa cita o arquivo que altera

## Path Conventions

Aplicação Flask na raiz, como em `plan.md`: `app.py`, `servidor/`, `templates/`, `tests/`, `alembic/`, `documentacao/`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependências e pastas da constituição 2.1.1

- [X] T001 Criar `servidor/__init__.py`, `tests/` e `alembic/` conforme a árvore de `specs/001-planejar-voo-visual/plan.md`
- [X] T002 Acrescentar em `requirements.txt` SQLAlchemy 2, psycopg 3, Alembic e pytest, mantendo Flask 3.0.0, requests 2.31.0 e reportlab 4.0.7
- [X] T003 [P] Criar `.env.example` na raiz só com os nomes `DATABASE_URL`, `SECRET_KEY`, `REDEMET_API_KEY`, `AISWEB_API_KEY` e `AISWEB_API_PASS`, sem valores

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Banco, modelos e aplicação. Nenhuma história começa antes disto.

**⚠️ CRITICAL**: Nenhuma história começa antes do fim desta fase.

- [X] T004 Inicializar Alembic em `alembic.ini` e `alembic/env.py`, lendo `DATABASE_URL` do ambiente
- [X] T005 [P] Criar em `servidor/modelos.py` as entidades com estas regras literais: Piloto.identificacao única e obrigatória; senha_hash obrigatória e nunca a senha em claro; senha original com no mínimo 8 caracteres; Aeronave.peso_max_decolagem_kg maior que peso_vazio_kg; Aerodromo.icao com quatro letras como chave; PlanoDeVoo.origem_icao e destino_icao obrigatórios, diferentes e existentes; PlanoDeVoo.piloto_id obrigatório; TentativaEntrada.identificacao e instante obrigatórios; cinco TentativaEntrada da mesma identificação em 15 minutos bloqueiam até 15 minutos depois da quinta
- [X] T006 Gerar a migração Alembic em `alembic/versions/` a partir de `servidor/modelos.py`
- [X] T007 Gravar em `servidor/semente.py` o Cessna 140 (vazio 404 kg, máximo de decolagem 658 kg, bagagem máxima 36 kg, braço da bagagem 2,03 m, uma vez só) e os aeródromos SBJD, SBAU, SBBU, SBML, SBDN, SBKP e SBRP, cada um com fonte
- [X] T008 Montar em `app.py` a fábrica Flask que lê o ambiente, abre o PostgreSQL e configura o cookie de sessão HttpOnly, SameSite=Lax e Secure fora de acesso local
- [X] T009 Criar `tests/conftest.py` com base de teste, semente e cliente HTTP

**Checkpoint**: Migração aplica, semente carrega, pytest coleta.

---

## Phase 3: User Story 1 - Montar e calcular o plano (Priority: P1) 🎯 MVP

**Goal**: Um piloto já identificado informa origem, destino, hora e dados particulares e recebe navegação, combustível e limites, com unidade e fonte.

**Independent Test**: Com o piloto inserido no teste e o manual do Cessna 140 disponível, `POST /planos` devolve o plano calculado. Peso acima de 658 kg fica inaceitável. Manual incompleto não grava.

### Tests for User Story 1

- [X] T010 [P] [US1] Escrever em `tests/test_calculo.py` os testes que falham: grandeza com unidade e fonte; peso acima de 658 kg marca o plano inaceitável e mostra o excesso; origem igual ao destino não grava; dado técnico ausente no manual não grava e diz qual dado falta

### Implementation for User Story 1

- [X] T011 [US1] Implementar navegação, combustível e limites em `servidor/calculo.py`, lendo os números só de `servidor/modelos.py` (Aeronave)
- [X] T012 [US1] Implementar `POST /planos` em `servidor/planos.py`: aeronave com manual, origem e destino diferentes e existentes, hora de partida, dados particulares obrigatórios (ocupantes, pesos, combustível a bordo, cada um com unidade); hora no passado só grava com confirmação
- [X] T013 [US1] Ligar `POST /planos` e o formulário em `app.py` e `templates/plano.html`, mostrando estado calculado ou inaceitável e o aviso de `documentacao/piloto.md` de que o resultado não autoriza o voo

**Checkpoint**: `tests/test_calculo.py` passa. O piloto de teste vê o plano sem carta, radar ou login ainda.

---

## Phase 4: User Story 2 - Entrar no espaço próprio (Priority: P1)

**Goal**: Cadastro e entrada com senha, espaço só do piloto, bloqueio e sessão que acaba.

**Independent Test**: Dois pilotos. O plano de um não abre para o outro. Senha curta não cadastra. A sexta tentativa no bloqueio recebe a mesma mensagem de uma identificação inexistente. Sessão encerrada não abre plano.

### Tests for User Story 2

- [X] T014 [P] [US2] Escrever em `tests/test_acesso.py` os testes que falham: senha com menos de 8 caracteres não cria Piloto; mensagem idêntica para identificação inexistente, senha errada e bloqueio; cinco TentativaEntrada em 15 minutos recusam a senha certa por mais 15 minutos; sair ou 8 horas sem uso impede abrir plano
- [X] T015 [P] [US2] Escrever em `tests/test_isolamento.py` o teste que falha: o piloto B não lista, não abre, não edita e não apaga o plano do piloto A, e a recusa não diz se o plano existe

### Implementation for User Story 2

- [X] T016 [US2] Implementar cadastro, entrada, saída, hash do Werkzeug e TentativaEntrada em `servidor/auth.py`
- [X] T017 [US2] Ligar `POST /cadastro`, `POST /entrar` e `POST /sair` em `app.py` e nas páginas `templates/cadastro.html` e `templates/entrar.html`
- [X] T018 [US2] Filtrar toda leitura e escrita de plano por `piloto_id` da sessão em `servidor/planos.py`

**Checkpoint**: `tests/test_acesso.py` e `tests/test_isolamento.py` passam. US1 continua passando.

---

## Phase 5: User Story 3 - Ver tempo, carta, radar e vento (Priority: P2)

**Goal**: O plano mostra meteorologia, carta WAC, radar e perfil de vento, ou indisponível quando a fonte falha.

**Independent Test**: Com origem, destino e hora, cada item aparece preenchido ou como indisponível. Nenhum valor é inventado. Sem chave, radar, carta e vento ficam indisponíveis e o resto do plano permanece.

### Tests for User Story 3

- [X] T019 [P] [US3] Escrever em `tests/test_tempo.py` os testes que falham: falha ou corpo vazio de METAR, TAF, radar, carta ou vento grava `indisponivel`; resposta sem dado não preenche valor; tempo limite de 8 segundos

### Implementation for User Story 3

- [X] T020 [US3] Implementar em `servidor/tempo.py` METAR e TAF no Aviation Weather Center, radar MaxCappi da REDEMET, carta WAC vigente do AISWEB e vento de área da REDEMET, cada um com estado `indisponivel` se a chave ou a rede falhar
- [X] T021 [US3] Gravar meteorologia, vento, carta e radar no plano dentro de `servidor/planos.py` na criação
- [X] T022 [US3] Mostrar rota, radar posicionado e o perfil de vento (direção, velocidade e efeito no voo) em `templates/plano.html` com Leaflet 1.9, sem fórmula de navegação no JavaScript

**Checkpoint**: `tests/test_tempo.py` passa com fontes simuladas. A tela distingue dado presente de indisponível.

---

## Phase 6: User Story 4 - Checklist e impressão (Priority: P2)

**Goal**: Checklist sugerido a partir do manual, marcável, e PDF com rota, horários, combustível, vento, tempo, checklist e aviso.

**Independent Test**: Um plano calculado gera checklist com fonte em cada item. O piloto marca um item. O PDF contém as partes do plano e o aviso. Item indisponível sai como indisponível no PDF.

### Tests for User Story 4

- [X] T023 [P] [US4] Escrever em `tests/test_pdf.py` os testes que falham: checklist nasce do manual com campo fonte; `POST /planos/{id}/checklist/{item}` marca só item do piloto da sessão; `GET /planos/{id}/pdf` inclui rota, horários, combustível, vento, resumo do tempo, checklist e o aviso de que não autoriza o voo

### Implementation for User Story 4

- [X] T024 [US4] Gerar ItemChecklist (ordem, texto, fonte, marcado começa falso) em `servidor/planos.py` a partir de Aeronave.itens_manutencao e da preparação de voo visual
- [X] T025 [US4] Montar o PDF em `servidor/pdf_plano.py` com reportlab
- [X] T026 [US4] Ligar `GET /planos/{id}/pdf` e `POST /planos/{id}/checklist/{item}` em `app.py` e a lista marcável em `templates/plano.html`

**Checkpoint**: `tests/test_pdf.py` passa. O PDF abre com o aviso.

---

## Phase 7: User Story 5 - Rever planos anteriores (Priority: P2)

**Goal**: Painel com os planos do piloto, edição que recalcula, exclusão só com confirmação.

**Independent Test**: Dois planos no painel, com origem, destino e hora. Editar a hora recalcula e busca tempo, vento, carta e radar de novo. Apagar sem `confirmar: true` mantém o plano. Confirmar remove da lista.

### Tests for User Story 5

- [X] T027 [P] [US5] Escrever em `tests/test_historico.py` os testes que falham: `GET /planos` só lista o piloto da sessão; `PUT /planos/{id}` recalcula e atualiza `atualizado_em`; `DELETE /planos/{id}` sem `confirmar: true` mantém o registro; com `confirmar: true` o plano deixa de abrir

### Implementation for User Story 5

- [X] T028 [US5] Implementar `GET /planos`, `GET /planos/{id}`, `PUT /planos/{id}` e `DELETE /planos/{id}` em `servidor/planos.py`, refazendo checklist se o texto mudar e buscando de novo as fontes externas na edição
- [X] T029 [US5] Criar o painel em `templates/painel.html` e ligar as rotas em `app.py`, com confirmação antes de apagar

**Checkpoint**: `tests/test_historico.py` passa. O painel reflete edição e exclusão na mesma visita.

---

## Phase 8: User Story 6 - Entender o plano na tela (Priority: P2)

**Goal**: A tela e o PDF mostram o que informar, o que é indisponível e o aviso, com o texto de `documentacao/piloto.md`.

**Independent Test**: A página do plano e o PDF contêm as três frases desse arquivo. O piloto não precisa de outro documento.

### Tests for User Story 6

- [X] T030 [P] [US6] Escrever em `tests/test_orientacao.py` o teste que falha: a resposta de `GET /planos/{id}` e o PDF contêm, vindos de `documentacao/piloto.md`, o que informar, o significado de indisponível e que o resultado não autoriza o voo

### Implementation for User Story 6

- [X] T031 [US6] Renderizar `documentacao/piloto.md` em `templates/plano.html` e em `servidor/pdf_plano.py`, sem copiar o texto para uma segunda constante

**Checkpoint**: `tests/test_orientacao.py` passa.

---

## Phase 9: User Story 7 - Subir o sistema pela documentação de operação (Priority: P2)

**Goal**: `documentacao/operacao.md` basta para preparar o PostgreSQL, apontar as chaves e subir o serviço, sem segredo escrito.

**Independent Test**: O arquivo não contém senha nem chave. Os comandos de migração, semente e subida batem com o que o repositório executa.

### Tests for User Story 7

- [X] T032 [P] [US7] Escrever em `tests/test_operacao_doc.py` o teste que falha se `documentacao/operacao.md` contiver valor de chave ou senha, e se não citar migração, semente e subida

### Implementation for User Story 7

- [X] T033 [US7] Completar em `documentacao/operacao.md` os comandos exatos de Alembic, `servidor/semente.py` e Flask, sem valores de `DATABASE_URL`, `SECRET_KEY`, `REDEMET_API_KEY`, `AISWEB_API_KEY` ou `AISWEB_API_PASS`

**Checkpoint**: `tests/test_operacao_doc.py` passa. Um operador segue só esse arquivo.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Conferir o conjunto sem abrir história nova

- [X] T034 Rodar `tests/` e corrigir falha que una as histórias, sem mudar regra já testada
- [X] T035 Percorrer `specs/001-planejar-voo-visual/quickstart.md` no navegador e anotar no fim de `documentacao/operacao.md` só o que divergir, sem colar segredo
- [X] T036 Retirar de `app.py` o uso de `cessna140.db` no caminho do produto novo, deixando o PostgreSQL como único banco de piloto, manual, aeródromo e plano

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: começa agora
- **Foundational (Phase 2)**: depende da Phase 1 e bloqueia todas as histórias
- **US1 (Phase 3)**: depende da Phase 2. Não depende de US2; o teste cria o piloto
- **US2 (Phase 4)**: depende da Phase 2. Filtra os planos criados em US1
- **US3 (Phase 5)**: depende de US1 (o plano já existe para receber tempo, carta, radar e vento)
- **US4 (Phase 6)**: depende de US1
- **US5 (Phase 7)**: depende de US1 e US2
- **US6 (Phase 8)**: depende de US1 e US4
- **US7 (Phase 9)**: depende da Phase 2; os comandos finais ficam estáveis depois de T006 e T007
- **Polish (Phase 10)**: depende das histórias que forem entrar na entrega

### User Story Dependencies

- **US1 (P1)**: piloto de teste, sem tela de login
- **US2 (P1)**: entrada real e isolamento; não muda a fórmula de US1
- **US3 (P2)**: enriquece o plano de US1
- **US4 (P2)**: checklist e PDF do plano de US1
- **US5 (P2)**: lista, edição e exclusão com a sessão de US2
- **US6 (P2)**: o texto já está em `documentacao/piloto.md`; a tarefa só o publica
- **US7 (P2)**: o rascunho já está em `documentacao/operacao.md`; a tarefa só completa os comandos

### Within Each User Story

- O teste da história fica vermelho antes da implementação
- Modelo e serviço antes da rota
- Rota antes da página

### Parallel Opportunities

- T003 em paralelo com T002
- T004 e T005 em paralelo
- T014 e T015 em paralelo
- Testes de histórias diferentes, em arquivos diferentes, em paralelo depois da Phase 2

---

## Parallel Example: User Story 2

```bash
# Os dois testes de acesso não compartilham arquivo:
# tests/test_acesso.py
# tests/test_isolamento.py
```

---

## Implementation Strategy

### MVP First (User Story 1, depois a porta)

1. Phase 1 e Phase 2
2. Phase 3 (US1) e parar: o cálculo se prova sozinho
3. Phase 4 (US2): o piloto entra de verdade e só vê o próprio plano
4. Esse par é o MVP demonstrável

### Incremental Delivery

5. US3 tempo, carta, radar e vento
6. US4 checklist e PDF
7. US5 painel, editar e apagar
8. US6 orientação na tela e no PDF
9. US7 operação sem segredo
10. Phase 10, quickstart no navegador

### Parallel Team Strategy

Depois da Phase 2, US1 e US2 podem andar juntos se quem faz US2 não editar `servidor/calculo.py`. US3 e US4 esperam o `POST /planos` de US1.

---

## Notes

- Marque `[x]` só na tarefa concluída
- Não reabra fórmula no JavaScript
- Não copie peso, bagagem ou braço do Cessna 140 para fora de `servidor/modelos.py` e da semente
- Chave só no ambiente, nunca em `documentacao/` nem em teste versionado

---

## Phase 11: Convergence

**Purpose**: Fechar o que a spec, o plano e a constituição ainda não encontram no código

- [ ] T037 CRITICAL Retirar `templates/index.html`: a página não é servida por `app.py`, mas guarda fórmula de navegação em JavaScript e o consumo 5,0 da semente per Constitution III (contradicts)
- [ ] T038 Ler em `servidor/tempo.py` direção, velocidade e fonte do produto de área da REDEMET somente quando a mensagem cobrir a rota; sem cobertura, manter `indisponivel`. Em `servidor/calculo.py`, não publicar velocidade em relação ao solo igual à de planejamento quando o vento está indisponível per FR-009 (partial)
- [ ] T039 Mostrar na tela do plano e no PDF o texto do METAR e do TAF quando a meteorologia estiver disponível, e manter o item indisponível, sem valor inventado, quando a fonte falhar per FR-004 (partial)
- [ ] T040 Em `servidor/tempo.py`, usar a carta WAC cuja área cubra a rota e gravar `indisponivel` quando nenhuma carta da resposta cobrir a região per FR-008 (partial)
