---
description: "Tarefas para auditar e corrigir funções, botões e camadas"
---

# Tasks: Auditoria de funções, botões e camadas

**Input**: Design documents from `specs/019-auditoria-funcoes-botoes/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Incluídos porque a especificação exige validar persistência, motivos de indisponibilidade, isolamento e largura em viewport móvel.

**Organization**: Tarefas agrupadas por história de usuário; alterações que compartilham `templates/plano.html` e `tests/test_tela_piloto.py` são sequenciadas.

## Format

- `[P]` identifica tarefas em arquivos distintos sem dependência pendente.
- `[US#]` rastreia tarefa a uma história da especificação.
- Cada tarefa tem checkbox, ID sequencial e caminho de arquivo.

## Path Conventions

- Aplicação Flask/Jinja no repositório: `app.py`, `servidor/`, `templates/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: Preparação compartilhada.

O Flask, o PostgreSQL, as dependências e os fixtures de teste já existem. Nenhuma inicialização ou dependência nova é necessária.

## Phase 2: Foundational

**Purpose**: Pré-requisitos para as histórias.

O acesso autenticado, o banco único e a infraestrutura de testes já atendem às histórias. Não criar migração nem alterar configuração externa.

## Phase 3: User Story 1 - Salvar o nome de exibição (Priority: P1) 🎯 MVP

**Goal**: Persistir o nome válido e mostrar confirmação somente após o commit.

**Independent Test**: Usar o cliente de teste isolado para verificar sucesso, erro de validação e isolamento entre pilotos.

### Tests for User Story 1

- [X] T001 [P] [US1] Em `tests/test_acesso.py`, verificar confirmação após POST HTML válido, ausência de sucesso para entrada inválida e preservação do contrato JSON.

### Implementation for User Story 1

- [X] T002 [US1] Em `app.py` e `templates/perfil.html`, emitir e apresentar confirmação transitória somente após `g.db.commit()`, preservando POST/Redirect/GET e a mensagem de validação existente.

**Checkpoint**: A confirmação aparece apenas após persistência e o perfil continua isolado pelo piloto autenticado.

## Phase 4: User Story 2 - Consultar as camadas do mapa (Priority: P1)

**Goal**: Apresentar motivos corretos de indisponibilidade sem alterar os gates das fontes.

**Independent Test**: Testar chave ausente, fonte sem dados válidos e plano antigo sem motivo; confirmar que a camada continua desligada.

### Tests for User Story 2

- [X] T003 [P] [US2] Em `tests/test_tempo.py` e `tests/test_tela_piloto.py`, cobrir motivo de chave REDEMET ausente, dados/limites inválidos, fonte indisponível e fallback para plano antigo sem `motivo`.

### Implementation for User Story 2

- [X] T004 [P] [US2] Em `servidor/tempo.py`, incluir motivos categorizados e seguros no JSON de radar para chave ausente, resposta sem cobertura válida e falha da fonte, sem expor exceções.
- [X] T005 [P] [US2] Em `templates/plano.html`, exibir o motivo devolvido pelo servidor; para JSON legado sem motivo, mostrar apenas indisponibilidade genérica verdadeira e preservar WAC/OpenAIP bloqueadas.

**Checkpoint**: A disponibilidade do radar e da OpenAIP continua condicionada aos gates existentes; nenhuma substituição silenciosa é introduzida.

## Phase 5: User Story 3 - Usar controles em telas estreitas (Priority: P2)

**Goal**: Manter todas as colunas da tabela acessíveis sem ampliar a página além da viewport.

**Independent Test**: Em 390 px, rolar a tabela internamente e confirmar que a largura do documento não supera a viewport; repetir em 1440 px.

### Tests for User Story 3

- [X] T006 [US3] Em `tests/test_tela_piloto.py`, verificar que a tabela de procedência mantém todos os cabeçalhos dentro de um contêiner com rolagem própria.

### Implementation for User Story 3

- [X] T007 [US3] Em `templates/plano.html`, envolver a tabela de 11 colunas em uma área com rolagem horizontal própria, sem remover colunas nem alterar os dados.

**Checkpoint**: Em 390 px e 1440 px, o mapa, as ações e todos os campos da tabela continuam acessíveis.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Auditar demais ações e validar o resultado integrado.

- [X] T008 [P] Em `documentacao/piloto.md`, atualizar somente as instruções de perfil e indisponibilidade das camadas, sem duplicar avisos didáticos.
- [X] T009 [P] Em `templates/entrar.html`, `templates/cadastro.html`, `templates/painel.html`, `templates/plano_novo.html`, `templates/plano.html`, `templates/perfil.html` e nos testes correspondentes, classificar cada ação primária como funcionando, indisponível com motivo ou falha reproduzível; não executar ações destrutivas.
- [X] T010 Em `specs/019-auditoria-funcoes-botoes/quickstart.md`, executar testes focados, auditoria não destrutiva e checagens em 390 px/1440 px; executar a suíte completa e registrar a falha de complexidade fora do escopo sem atribuir causa.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma tarefa.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **US1 (Phase 3)**: independente; pode ser validada sem completar outras histórias.
- **US2 (Phase 4)**: independente de US1; seus testes precedem as alterações em servidor e template.
- **US3 (Phase 5)**: após US2, pois ambas alteram `templates/plano.html` e `tests/test_tela_piloto.py`.
- **Polish (Phase 6)**: após as três histórias.

### User Story Dependencies

- **US1 (P1)**: sem dependência de outra história.
- **US2 (P1)**: sem dependência de US1; compartilhará arquivos com US3.
- **US3 (P2)**: depende de US2 terminar para evitar conflito nos arquivos do mapa.

### Within Each User Story

- Os testes precedem a implementação.
- US1: T001 → T002.
- US2: T003 → T004/T005; T004 e T005 podem ocorrer em paralelo após o contrato de motivos ficar definido.
- US3: T006 → T007.

### Parallel Opportunities

- T001 e T003 podem ser trabalhadas em paralelo, pois usam testes distintos.
- Depois de T003, T004 e T005 podem ser trabalhadas em paralelo, pois alteram arquivos diferentes.
- T008 e T009 podem ocorrer em paralelo durante a fase final.

## Parallel Example: User Story 1

```text
T001: adicionar asserções de confirmação e validação em tests/test_acesso.py
T002: implementar confirmação em app.py e templates/perfil.html após T001
```

## Parallel Example: User Story 2

```text
T003: escrever testes de motivo em tests/test_tempo.py e tests/test_tela_piloto.py
Após T003:
T004: categorizar indisponibilidade em servidor/tempo.py
T005: apresentar motivo em templates/plano.html
```

## Parallel Example: User Story 3

```text
T006: adicionar verificação da tabela responsiva em tests/test_tela_piloto.py
T007: conter a rolagem da tabela em templates/plano.html após T006
```

## Implementation Strategy

1. Implementar e validar US1 primeiro como incremento MVP.
2. Implementar US2 preservando todos os gates externos.
3. Implementar US3 depois de concluir US2 para evitar conflito no template e teste compartilhados.
4. Auditar demais controles e executar a validação integrada definida em `quickstart.md`.
5. Não considerar a WAC, OpenAIP ou radar funcionais quando dependências externas continuam ausentes.
