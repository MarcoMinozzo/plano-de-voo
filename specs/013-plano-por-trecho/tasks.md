---
description: "Tarefas para alinhar a tela do plano calculado à experiência aprovada"
---

# Tasks: Tela do plano organizada por trecho

**Input**: Design documents from `specs/013-plano-por-trecho/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/tela-plano.md`, `quickstart.md`

**Tests**: Requeridos para as interações de abas/mapa, dados estruturados de METAR, indisponibilidade e acessibilidade descritos na especificação.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem conflito de arquivos ou dependências.
- **[Story]**: história relacionada (`US1`, `US2`, `US3`).
- Cada tarefa indica os caminhos exatos envolvidos.

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: Preparação. Flask, PostgreSQL, Leaflet, Tailwind e os serviços meteorológicos já existem; não há dependência nova nem setup pendente.

## Phase 2: Foundational

**Purpose**: Pré-requisitos compartilhados. Planos, trechos persistidos, aeródromos, propriedade por piloto e JSON meteorológico já existem; nenhuma migração ou alteração de cálculo é necessária.

## Phase 3: User Story 1 - Consultar cada trecho em sua própria ficha (Priority: P1) 🎯 MVP

**Goal**: Manter o resumo acima e apresentar uma ficha identificada e selecionável para cada trecho, sem checklist interativo na tela.

**Independent Test**: Abrir planos de um e vários trechos, selecionar fichas e verificar conteúdo, estado acessível, ordem visual, avisos e ausência de ações de checklist.

### Tests for User Story 1

- [X] T001 [US1] Adicionar regressões para resumo fixo, uma ficha por trecho, seleção acessível e ausência de checklist na tela em `tests/test_casca_visual.py` e `tests/test_tela_piloto.py`.

### Implementation for User Story 1

- [X] T002 [US1] Implementar navegação progressiva por fichas e painéis por trecho e retirar o checklist interativo da tela em `templates/plano.html`; redirecionar atualizações de checklist sem âncora órfã em `app.py`.

## Phase 4: User Story 2 - Consultar o mapa do trecho ativo (Priority: P1)

**Goal**: Atualizar o mapa para mostrar exclusivamente o trecho selecionado, com estado explícito das fontes e radar independente.

**Independent Test**: Alternar entre trechos e camadas em plano com vários trechos; verificar somente dois endpoints e uma linha do trecho ativo, WAC indisponível sem os gates, radar inicialmente desligado e OpenAIP identificada corretamente.

### Tests for User Story 2

- [X] T003 [US2] Adicionar regressões de coordenadas por trecho, mapa limitado ao trecho ativo, estado indisponível da WAC e alternância independente de base/radar em `tests/test_tela_piloto.py`.

### Implementation for User Story 2

- [X] T004 [US2] Preparar em `app.py` pares de coordenadas correspondentes aos trechos persistidos, sem alterar rota, ordem ou cálculo.
- [X] T005 [US2] Atualizar em `templates/plano.html` o mapa para o trecho ativo, manter uma instância Leaflet, ajustar enquadramento ao trocar ficha e expor ruas, WAC indisponível, OpenAIP e radar independente.

## Phase 5: User Story 3 - Ler a meteorologia do trecho (Priority: P1)

**Goal**: Mostrar METAR/TAF da saída e chegada do trecho ativo, decodificando em português os campos METAR estruturados disponíveis e mantendo seu original.

**Independent Test**: Usar respostas simuladas com campos presentes, nulos e códigos não suportados; confirmar rótulos/unidades/source, original intacto, TAF bruto e indisponibilidades por aeródromo.

### Tests for User Story 3

- [X] T006 [US3] Adicionar testes para campos, unidades, horário e texto bruto da resposta AWC em `tests/test_tempo.py`, incluindo valores ausentes e códigos METAR sem tradução suportada; testar consulta única por aeródromo distinto em `tests/test_rota.py`.

### Implementation for User Story 3

- [X] T007 [US3] Capturar campos estruturados opcionais em `servidor/tempo.py` e obter METAR/TAF uma vez por aeródromo distinto da rota em `servidor/planos.py`, mantendo `rawOb`, `reportTime`, `fonte` e indisponibilidades.
- [X] T008 [US3] Preparar em `servidor/tempo.py` rótulos METAR em português para os campos suportados e estados explícitos para os não decodificados; manter `linhas_boletim` e o contrato do PDF inalterados.
- [X] T009 [US3] Preparar em `app.py` e exibir na ficha ativa os boletins de saída/chegada do trecho, com campos METAR em português, texto original, TAF bruto e indisponibilidades corretas em `templates/plano.html` e `tests/test_tela_piloto.py`.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentar e validar o fluxo integrado sem alterar cálculo, propriedade do plano ou PDF.

- [X] T010 [P] Atualizar `documentacao/piloto.md` para explicar fichas por trecho, METAR apresentado em português e estados indisponíveis do mapa.
- [X] T011 Executar `uv run pytest --no-cov tests/test_tela_piloto.py tests/test_tempo.py tests/test_casca_visual.py tests/test_rota_pdf.py -q` e `git diff --check`; corrigir somente regressões da feature em `app.py`, `servidor/tempo.py`, `templates/plano.html` e nos testes correspondentes.
- [ ] T012 Validar a navegação, foco, mapa por trecho, camadas e responsividade em 390 px e 1440 px, por teclado e toque, conforme `specs/013-plano-por-trecho/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; sem dependências.
- **Foundational (Phase 2)**: já atendido; sem tarefas bloqueadoras.
- **US1 (Phase 3)**: T001 precede T002.
- **US2 (Phase 4)**: depende da seleção de ficha da US1; T003 precede T004 e T005; T004 precede a integração do mapa em T005.
- **US3 (Phase 5)**: T006 precede T007/T008; T009 integra dados do servidor à ficha e depende de T002, T004, T005 e T007.
- **Polish (Phase 6)**: T010 pode ser executada em paralelo às validações; T011 e T012 verificam o resultado integrado.

### User Story Dependencies

- **US1 (P1)**: independente; estabelece a estrutura e a seleção das fichas.
- **US2 (P1)**: depende de US1 para identificar o trecho ativo; não altera cálculo.
- **US3 (P1)**: depende do contexto de ficha da US1; não depende do mapa da US2.

### Parallel Opportunities

- Nenhuma tarefa de código é marcada `[P]`: as mudanças de UI compartilham `templates/plano.html`, e os testes compartilham `tests/test_tela_piloto.py`.
- T010, que altera somente `documentacao/piloto.md`, pode ocorrer em paralelo com validações sem editar código ou testes.

## Implementation Strategy

1. Implementar e testar US1: resumo fixo, fichas acessíveis e remoção do checklist interativo da tela.
2. Implementar US2: passar endpoints por trecho e limitar o mapa à ficha ativa; manter WAC indisponível enquanto os gates existentes não forem comprovados.
3. Implementar US3: preservar texto bruto e adicionar apresentação dos campos AWC disponíveis, sem inferência; TAF continua bruto.
4. Executar testes focados e a verificação manual responsiva; conferir que o PDF e o cálculo permanecem inalterados.

## Notes

- A implementação não aprova nem disponibiliza a WAC; os gates da feature 009 continuam obrigatórios.
- Campos de METAR nulos ou desconhecidos não recebem valor ou tradução inventados.
- Todos os itens seguem o formato de checklist com ID sequencial, história quando aplicável e caminho de arquivo.
