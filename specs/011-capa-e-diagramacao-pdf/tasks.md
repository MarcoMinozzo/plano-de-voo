---
description: "Tarefas para nome de perfil e relatório PDF diagramado"
---

# Tasks: Capa e diagramação do PDF de voo

**Input**: Design documents from `specs/011-capa-e-diagramacao-pdf/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/perfil-e-pdf.md`, `quickstart.md`

**Tests**: Solicitados na especificação para perfil, migração, acesso e
conteúdo do PDF.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo sem conflito de arquivos ou dependências.
- **[Story]**: história relacionada (`US1`).
- Cada tarefa indica os caminhos exatos envolvidos.

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `alembic/`,
  `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: Preparação do projeto.

Dependências, ambiente de testes, PostgreSQL, Alembic, ReportLab e Tailwind já
estão configurados; não há setup nem dependência nova.

## Phase 2: Foundational

**Purpose**: Pré-requisitos compartilhados.

A autenticação e a checagem de propriedade do plano já existem. Não alterar
essas regras nem criar infraestrutura paralela.

## Phase 3: User Story 1 - Identificar e consultar o relatório do voo (Priority: P1) 🎯 MVP

**Goal**: Manter um nome de exibição por piloto e gerar relatório técnico
imprimível com capa e conteúdo completo paginado.

**Independent Test**: Cadastrar/editar um nome, gerar PDF de plano próprio
direto e com escalas e conferir capa, fontes, avisos e páginas em A4.

### Tests for User Story 1

- [X] T001 [P] [US1] Adicionar testes para nome obrigatório, aparado e limitado a 160 caracteres, backfill, edição própria e recusa de outro piloto em `tests/test_acesso.py`, `tests/test_migracao_perfil.py` e `tests/test_casca_visual.py`.
- [X] T002 [P] [US1] Adicionar testes de capa, nome atual, rota com escalas, data/fuso, logo, paginação e conteúdo DEMO preservado em `tests/test_rota_pdf.py`.

### Implementation for User Story 1

- [X] T003 [US1] Adicionar `Piloto.nome_exibicao` obrigatório com limite de 160 caracteres e migração encadeada após `d1e2f3a4b5c6` que preenche contas antigas com `identificacao` em `servidor/modelos.py` e nova revisão em `alembic/versions/`.
- [X] T004 [US1] Exigir, aparar e validar nome de exibição no cadastro mantendo identificação/senha independentes em `servidor/auth.py`, `app.py` e `templates/cadastro.html`.
- [X] T005 [US1] Criar edição autenticada do próprio nome, com validação e retorno explícito, e link no menu em `app.py`, `templates/perfil.html` e `templates/base.html`.
- [X] T006 [US1] Reorganizar o PDF com capa que usa o nome atual, emblema, rota ordenada completa e data/hora com fuso, e diagramar o conteúdo integral com paginação sem alterar a checagem de propriedade em `servidor/pdf_plano.py` e `app.py`.
- [X] T007 [US1] Documentar edição do nome e conteúdo do PDF em `documentacao/piloto.md` e recompilar estilos após adicionar os templates em `static/css/tailwind.css`.

**Checkpoint**: Nome de perfil editável e PDF identificável, legível e completo
em casos diretos, com escalas e DEMO.

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validação final da história.

- [X] T008 Executar `uv run pytest --no-cov tests/test_acesso.py tests/test_casca_visual.py tests/test_rota_pdf.py tests/test_migracao_perfil.py` e `git diff --check`; corrigir regressões relacionadas à feature.
- [X] T009 Conferir PDFs de rota direta, com escalas e DEMO em leitor e impressão A4 conforme `specs/011-capa-e-diagramacao-pdf/quickstart.md`, incluindo quebras, margens, hierarquia, fuso, aviso e procedência.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; sem tarefa.
- **Foundational (Phase 2)**: já atendido; sem tarefa bloqueadora.
- **User Story 1 (Phase 3)**: T001 e T002 precedem a implementação. T003 precede
  cadastro, perfil e PDF; T004, T005 e T006 editam `app.py` e devem ser
  sequenciais. T007 depende dos templates prontos.
- **Polish (Phase 4)**: depende da história implementada.

### User Story Dependencies

- **User Story 1 (P1)**: única história e MVP; sem dependência de outra história.

### Parallel Opportunities

- T001 e T002 podem ser escritos em paralelo em arquivos de teste diferentes.
- Após T003, T004, T005 e T006 devem ser sequenciais por compartilharem
  `app.py`; T007 pode rodar após T005.
- Não paralelizar tarefas que editam o mesmo arquivo ou migração.

## Parallel Example: User Story 1

```text
Task: T001 — testes de cadastro, migração e edição em tests/test_acesso.py e tests/test_migracao_perfil.py
Task: T002 — testes do relatório em tests/test_rota_pdf.py
```

## Implementation Strategy

1. Criar os testes de perfil/migração e PDF, confirmando que falham antes da
   implementação.
2. Adicionar e migrar o nome de exibição preservando credenciais.
3. Implementar cadastro e edição própria antes de integrar o valor à capa.
4. Diagramar o relatório mantendo todo o conteúdo obrigatório.
5. Executar testes focados e revisar manualmente três PDFs em A4.

## Notes

- [P] indica arquivos sem conflito ou dependência pendente.
- A migração faz backfill; downgrade remove o campo e perde nomes editados.
- Não instalar dependências, alterar cálculos ou persistir PDFs.

## Phase 5: Convergence

- [X] T010 Adicionar um teste de que outra conta autenticada recebe `404` ao tentar baixar o PDF de um plano alheio em `tests/test_rota_pdf.py` (partial).
