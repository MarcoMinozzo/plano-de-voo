---
description: "Tarefas de implementação da integração Tailwind"
---

# Tasks: Integrar Tailwind CSS

**Input**: Design documents from `/specs/008-integrar-tailwind/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, constitution 5.1.0

**Tests**: Incluídos porque a especificação exige preservar a casca e os fluxos do piloto. Os testes novos da folha devem falhar antes da integração.

**Organization**: Toolchain e entrada CSS primeiro; depois integração e migração por grupos de telas; por fim, fluxos, documentação e conferência visual.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo, pois altera arquivos distintos e não depende de tarefa incompleta
- **[Story]**: História da spec (US1 ou US2)
- Cada tarefa indica o caminho exato dos arquivos

## Phase 1: Setup

**Purpose**: Adicionar o build frontend sem interferir no runtime Python

- [X] T001 [P] Criar `package.json` com `tailwindcss` e `@tailwindcss/cli` 4.3.5 em `devDependencies`, scripts `css:build` e `css:watch`, e gerar `package-lock.json`
- [X] T002 [P] Atualizar `.gitignore` para ignorar `node_modules/`, mantendo rastreável a folha compilada em `static/css/tailwind.css`

---

## Phase 2: Foundational

**Purpose**: Declarar tema e fonte de classes usados por todas as páginas

- [X] T003 Criar `static/css/input.css` com tokens de cor da casca, imports de tema/utilitários sem Preflight e fonte explícita `templates/`

**Checkpoint**: A entrada CSS existe, a descoberta de Jinja está definida e nenhuma camada de reset global será aplicada.

---

## Phase 3: User Story 1 - Estilizar as telas com Tailwind (Priority: P1) 🎯 MVP

**Goal**: As páginas usam Tailwind para reproduzir a casca aprovada e permitir estilização futura.

**Independent Test**: Build local gera utilitários usados pelos templates; páginas carregam a folha gerada e mantêm a casca em tela móvel e desktop.

### Tests for User Story 1

- [X] T004 [P] [US1] Em `tests/test_casca_visual.py`, exigir a referência local à folha compilada e ao menos um utilitário de template presente em `static/css/tailwind.css`; confirmar que o teste falha antes da integração

### Implementation for User Story 1

- [X] T005 [US1] Em `templates/base.html`, carregar a folha local, remover o bloco de estilos inline e migrar fundo, véu, cabeçalho, navegação, conteúdo e elementos comuns para utilitários Tailwind, mantendo os hooks semânticos
- [X] T006 [P] [US1] Em `templates/entrar.html` e `templates/cadastro.html`, migrar cards, campos e botões para utilitários, mantendo os hooks de formulário e as mensagens atuais
- [X] T007 [P] [US1] Em `templates/plano_novo.html`, migrar card, campos, aviso e ampulheta para utilitários sem alterar conteúdo ou lógica JavaScript
- [X] T008 [P] [US1] Em `templates/painel.html` e `templates/recusa.html`, migrar o conteúdo e a tabela para utilitários sem alterar navegação ou textos
- [X] T009 [P] [US1] Em `templates/plano.html`, migrar resumo, abas, tabelas, checklist e mapa para utilitários, mantendo integrações Leaflet e hooks existentes
- [X] T010 [US1] Executar `npm run css:build` para gerar `static/css/tailwind.css` e confirmar que os utilitários condicionais Jinja usados nas páginas estão incluídos

**Checkpoint**: A folha Tailwind está sendo servida localmente e a casca visual continua equivalente.

---

## Phase 4: User Story 2 - Preservar os fluxos do piloto (Priority: P1)

**Goal**: A migração visual não altera entrada, formulário, espera, navegação, abas, impressão ou saída.

**Independent Test**: Executar os testes de casca, tela, PDF e planejamento com a nova folha e confirmar os mesmos estados e ações.

### Tests for User Story 2

- [X] T011 [US2] Ajustar `tests/test_casca_visual.py`, `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py` apenas onde seletores dependem da classe HTML exata e validar entrada, envio, menu, abas e impressão

**Checkpoint**: Fluxos existentes continuam cobertos sem acoplamento a uma ordem exata de classes CSS.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentar e validar a adoção frontend de ponta a ponta

- [X] T012 Atualizar `documentacao/operacao.md` e `specs/008-integrar-tailwind/quickstart.md` com instalação via `npm ci`, build, watcher e execução sem watcher
- [X] T013 Executar `npm ci`, `npm run css:build`, `uv run pytest --no-cov tests/test_casca_visual.py tests/test_tela_piloto.py tests/test_rota_pdf.py` e `git diff --check`; abrir telas em viewport móvel e desktop e corrigir regressões nos arquivos correspondentes

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 e T002 não dependem uma da outra.
- **Foundational (Phase 2)**: T003 pode começar após T001; bloqueia a compilação e as histórias.
- **US1 (Phase 3)**: T004 pode ser escrito após a fundação; implementação começa após T003. T005–T009 usam arquivos separados e podem rodar em paralelo depois de T004; T010 depende de todas as migrações de template.
- **US2 (Phase 4)**: T011 depende de US1 para verificar o resultado integrado.
- **Polish (Phase 5)**: T012 pode ser feito em paralelo com US1; T013 depende de todos os trabalhos anteriores.

### User Story Dependencies

- **US1 (P1)**: Depende do Setup e da entrada CSS; nenhuma dependência de US2.
- **US2 (P1)**: Depende de US1, pois valida os fluxos após a migração de estilos.

### Parallel Opportunities

- T001 e T002 alteram arquivos diferentes.
- T006, T007, T008 e T009 podem ser distribuídas em paralelo depois de T004/T005, pois cada tarefa trabalha em templates distintos.
- T012 pode ser escrito enquanto os templates são migrados.

### Parallel Example: Migração de telas US1

```text
Após T004 e com a entrada CSS de T003 pronta:
T006 — templates/entrar.html e templates/cadastro.html
T007 — templates/plano_novo.html
T008 — templates/painel.html e templates/recusa.html
T009 — templates/plano.html
```

## Implementation Strategy

1. Completar Setup e Foundation; validar que CLI e fontes Jinja funcionam.
2. Escrever T004 antes da integração e confirmar a falha esperada.
3. Migrar os templates mantendo os hooks que o JavaScript e os testes usam.
4. Gerar CSS e validar a casca (US1).
5. Executar regressão dos fluxos do piloto (US2).
6. Documentar os comandos e fazer conferência visual em viewport estreito e desktop.

## Notes

- Não adicionar dependência Python ou alterar o `requirements.txt`.
- Não habilitar Preflight nesta migração, nem alterar a aparência deliberadamente.
- Não remover a folha compilada do Git: Flask deve servir o asset sem npm em runtime.
- Não reconstruir nomes de classes com fragmentos Jinja; classes condicionais devem ser tokens completos no template.

## Phase 6: Convergence

- [X] T014 Restaurar as classes Tailwind do link de navegação “Imprimir voo” no bloco `menu_imprimir` de `templates/plano.html` per FR-003 (partial)
- [X] T015 Aplicar utilitários Tailwind ao checkbox `confirmar_hora` em `templates/plano_novo.html`, preservando seu comportamento per FR-003 (partial)
- [X] T016 Conferir visualmente `cadastro`, `plano_novo`, `painel`, `plano` e `recusa` em Chrome nos viewports móvel e desktop per US1/AC3, SC-003 (partial)
