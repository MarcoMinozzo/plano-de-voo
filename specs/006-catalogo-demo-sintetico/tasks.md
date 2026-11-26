---
description: "Tarefas para o catálogo sintético isolado para DEMO"
---

# Tasks: Catálogo sintético isolado para DEMO

**Input**: Design documents from `specs/006-catalogo-demo-sintetico/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/catalogo-aeronaves.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode ser executada em paralelo, em arquivos distintos e sem dependência pendente
- **[Story]**: história relacionada (`US1`, `US2`)
- Todos os caminhos de arquivo são relativos à raiz do repositório.

## Phase 1: Setup

**Purpose**: Nenhuma dependência ou scaffold novo é necessário; usar a estrutura Flask, `.venv`, PostgreSQL e Alembic existentes.

## Phase 2: Foundational

**Purpose**: Criar a resolução de ambiente e o esquema de procedência de que ambas as histórias dependem.

- [X] T001 [P] Escrever testes de seleção explícita do banco DEMO, ambiente permitido e recusa de URL ausente/igual em `tests/test_ambiente_demo.py`.
- [X] T002 [P] Escrever testes da procedência sintética e da ausência de data editorial em `tests/test_catalogo_aeronaves.py`.
- [X] T003 Implementar `resolver_ambiente` em `servidor/ambiente.py`; exigir `APP_ENV=development`, `DEMO_MODE=1` e `DATABASE_URL_DEMO` distinto; não conectar nem recorrer à URL normal.
- [X] T004 Atualizar `servidor/modelos.py` e criar migração Alembic em `alembic/versions/` para permitir `tipo_fonte="sintetica"` e `data_publicacao` nula sem enfraquecer os requisitos de fontes oficiais/secundárias.
- [X] T005 Atualizar `app.py`, `alembic/env.py` e `servidor/catalogo.py` para resolver a mesma URL validada antes de abrir o banco; manter `servidor/semente.py` exclusivamente na base normal.

**Checkpoint**: a configuração normal permanece inalterada; o modo DEMO não pode inicializar sem uma base própria e segura.

## Phase 3: User Story 1 - Abrir o catálogo DEMO (Priority: P1)

**Goal**: Disponibilizar vinte perfis fictícios selecionáveis, com procedência explícita e cálculo no servidor.

**Independent Test**: Carregar a semente duas vezes no banco DEMO e obter exatamente vinte perfis genéricos completos; nenhum dado de navegação é criado pela semente.

### Tests for User Story 1

- [X] T006 [P] [US1] Testar vinte perfis, unidades, perfil de cruzeiro pareado e idempotência da semente DEMO em `tests/test_semente_demo.py`.
- [X] T007 [P] [US1] Testar aceitação da procedência sintética somente em DEMO e recusa de rota sem ROTAER oficial vigente em `tests/test_catalogo_aeronaves.py` e `tests/test_rota.py`.
- [X] T008 [P] [US1] Testar identificação sintética e aviso não operacional na seleção, resultado e PDF em `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py`.

### Implementation for User Story 1

- [X] T009 [US1] Criar `servidor/semente_demo.py` com vinte nomes genéricos e seis valores técnicos por perfil; associar fontes `sintetica`, usar apenas a base DEMO e não apagar registros existentes.
- [X] T010 [US1] Atualizar `servidor/modelos.py`, `servidor/proveniencia.py` e `servidor/catalogo.py` para reconhecer `sintetica` somente quando explicitamente permitido; manter falso por padrão e nunca exigir data editorial para uma fonte sintética.
- [X] T011 [US1] Propagar o modo DEMO por `app.py` e `servidor/planos.py`; permitir rota somente com emenda ROTAER oficial vigente no armazenamento DEMO e manter vento/meteo/pôr do sol sujeitos às fontes existentes.
- [X] T012 [US1] Adicionar rótulo DEMO e aviso de não uso operacional em `templates/plano_novo.html`, `templates/plano.html` e `servidor/pdf_plano.py`, incluindo a procedência por campo.

**Checkpoint**: catálogo DEMO e cálculos são testáveis sem ativar o modo normal nem gerar dados de navegação.

## Phase 4: User Story 2 - Impedir mistura com dados de produção (Priority: P1)

**Goal**: Demonstrar que inicialização, seleção, cálculo e carga normal nunca usam os perfis sintéticos.

**Independent Test**: Tentar ativar DEMO em produção, com URL ausente e com URL compartilhada; cada tentativa falha antes de criar conexão. No modo normal, perfil sintético não aparece nem pode ser calculado.

### Tests for User Story 2

- [X] T013 [P] [US2] Testar bloqueio em produção, URL DEMO ausente/compartilhada e ausência de fallback em `tests/test_ambiente_demo.py`.
- [X] T014 [P] [US2] Testar que perfis sintéticos no armazenamento normal não aparecem em `/aeronaves` nem passam por `/planos` em `tests/test_catalogo_aeronaves.py` e `tests/test_rota.py`.

### Implementation for User Story 2

- [X] T015 [US2] Corrigir os fluxos de configuração e validação em `servidor/ambiente.py`, `app.py`, `servidor/catalogo.py` e `servidor/planos.py` para satisfazer os testes sem fallback ou aceitação sintética no modo normal.

**Checkpoint**: nenhum perfil sintético pode ser usado fora do modo DEMO em desenvolvimento.

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T016 [P] Documentar variáveis, migração, carga oficial ROTAER no banco DEMO e execução do modo restrito em `documentacao/operacao.md`.
- [X] T017 [P] Explicar o rótulo DEMO e o aviso não operacional em `documentacao/piloto.md`.
- [X] T018 **Supersedido por 015**: o quickstart dependia de `DATABASE_URL_DEMO`, removida do runtime pela decisão de banco único. A suíte completa atual passou (136 testes); mutação: 68,4% (348/509), acima do piso de 56%. O fluxo antigo de DEMO não foi executado nem é declarado validado.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: nenhuma mudança de dependência.
- **Foundational (Phase 2)**: bloqueia as duas histórias.
- **US1 e US2**: começam após a fundação; US1 entrega o catálogo, US2 verifica a barreira de produção. A alteração de configuração de T015 depende de T003 e T005.
- **Polish (Phase 5)**: após a implementação e testes das duas histórias.

### User Story Dependencies

- **US1 (P1)**: depende da fundação para banco separado e procedência sintética; não depende de US2.
- **US2 (P1)**: depende da resolução de ambiente da fundação; seus testes podem ser preparados em paralelo com US1.

### Parallel Opportunities

- T001 e T002 são independentes.
- T006, T007 e T008 podem ser preparados em paralelo, em arquivos de teste distintos.
- T016 e T017 podem ser executados em paralelo.

## Implementation Strategy

1. Concluir a fundação: resolver ambiente e atualizar o esquema.
2. Entregar US1: semear vinte perfis e tornar procedência/cálculo DEMO explícitos.
3. Entregar US2: verificar bloqueio de produção e inelegibilidade no modo normal.
4. Concluir documentação e executar os testes focados e a suíte completa.

**MVP**: US1 e US2 juntas; o catálogo só é seguro quando os dados DEMO podem ser consultados e sua separação de produção está comprovada.
