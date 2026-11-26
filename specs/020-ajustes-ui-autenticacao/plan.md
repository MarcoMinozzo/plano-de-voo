# Implementation Plan: Aprimorar cartões de autenticação

**Branch**: `main` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/020-ajustes-ui-autenticacao/spec.md`

## Summary

Atualizar somente a apresentação das telas de login e cadastro: logos maiores, cartões centralizados na viewport, título de login não visível, botão renomeado para “Acessar”, atribuição abaixo de “Criar acesso” e espaçamento reforçado entre senha e botão. Reutilizar o layout Flask/Jinja e Tailwind já existentes, preservando integralmente o fluxo de autenticação e a experiência em telas estreitas.

## Technical Context

**Language/Version**: Python 3.10+ com HTML/Jinja e CSS.

**Primary Dependencies**: Flask e Tailwind CSS já configurados; nenhuma dependência nova.

**Storage**: N/A; não há dados persistidos nesta mudança.

**Testing**: pytest focado em `tests/test_casca_visual.py` e `tests/test_acesso.py`; compilação Tailwind; inspeção visual das rotas `/entrar` e `/cadastro` em 390 px e 1440 px.

**Target Platform**: Navegadores móveis e desktop servidos pela aplicação Flask.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Não adicionar requisições ou scripts de runtime; renderização permanece local no fluxo existente.

**Constraints**: Preservar campos, validação, POST do login/cadastro, texto alternativo e proporção do logo. Centralizar sem cortar formulários quando a altura for pequena; permitir rolagem vertical nesses casos. Manter a atribuição apenas no cartão de login.

**Scale/Scope**: Duas páginas públicas de autenticação, um layout base compartilhado, a folha de estilo local e testes visuais existentes.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são preparados antes de alterar `templates/` ou `static/`. |
| II. Limite educacional | PASS | O aviso didático não é alterado nem removido. |
| III. Cálculo no servidor | PASS | Não há cálculo ou lógica de domínio nesta mudança. |
| IV. Unidades, fonte e indisponibilidade | PASS | Não há grandezas nem fontes de dados aeronáuticos envolvidas. |
| V. Pilha pequena e banco relacional | PASS | Sem banco, migração, segredo, integração ou dependência nova. |
| Segurança do acesso | PASS | Campos, validação, autenticação e sessões permanecem inalterados. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation (this feature)

```text
specs/020-ajustes-ui-autenticacao/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── cartoes-autenticacao.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
templates/
├── base.html
├── entrar.html
└── cadastro.html
static/css/
├── input.css
└── tailwind.css
tests/
├── test_casca_visual.py
└── test_acesso.py
```

**Structure Decision**: Reutilizar os templates e a compilação Tailwind existentes. Testar a estrutura renderizada pelo cliente Flask e complementar com inspeção visual; não criar componente ou camada de autenticação paralela.

## Phase 0: Outline & Research

Decisões e fatos de implementação estão registrados em [research.md](./research.md). Não há dependência externa, dado persistido ou incerteza técnica que exija pesquisa externa.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md): confirma que não há entidade nem estado persistido novo.
- [contracts/cartoes-autenticacao.md](./contracts/cartoes-autenticacao.md): define conteúdo, proporções, alinhamento e preservação do fluxo de login/cadastro.
- [quickstart.md](./quickstart.md): lista comandos e inspeções visuais para validar o resultado.
- Constituição reavaliada após o desenho: PASS; alteração restrita à apresentação, sem efeitos em autenticação ou dados.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
