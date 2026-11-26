# Implementation Plan: Logo centralizado no login e cadastro

**Branch**: `main` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/016-logo-login-cadastro/spec.md`

## Summary

Reutilizar o emblema existente no cartão das telas de entrar e cadastro, acima do título, centralizado e com 86,4 px de largura. Remover o logo do cabeçalho somente nessas duas telas; preservar o cabeçalho autenticado e o restante dos formulários.

## Technical Context

**Language/Version**: HTML/Jinja e CSS, aplicação Flask existente

**Primary Dependencies**: Tailwind CSS 4 já configurado; nenhuma dependência nova

**Storage**: N/A; não há alteração de dados

**Testing**: pytest focado em `tests/test_casca_visual.py`; compilação Tailwind; inspeção manual em navegador

**Target Platform**: Navegadores desktop e mobile

**Project Type**: Aplicação web Flask

**Performance Goals**: Sem impacto mensurável; usa a imagem já servida localmente

**Constraints**: Preservar proporção e texto alternativo do emblema; não alterar autenticação, navegação ou páginas além das duas solicitadas

**Scale/Scope**: Duas páginas públicas, cabeçalho compartilhado e um teste visual

## Constitution Check

- **Especificação antes do código**: PASS — spec, plano e tarefas são produzidos antes da implementação.
- **Limite educacional e avisos**: PASS — nenhum conteúdo ou cálculo do plano é alterado.
- **Cálculo no servidor**: PASS — mudança exclusivamente visual.
- **Unidades e fonte explícitas**: PASS — não há grandeza ou dado aeronáutico novo.
- **Pilha pequena**: PASS — reutiliza asset e Tailwind já existentes, sem dependência ou migração.
- **Acesso e segurança**: PASS — preserva rotas e formulários.

## Project Structure

### Documentation (this feature)

```text
specs/016-logo-login-cadastro/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md              # gerado por speckit-tasks
```

### Source Code

```text
templates/
├── base.html
├── entrar.html
└── cadastro.html
static/
└── css/
    ├── input.css
    └── tailwind.css
tests/
└── test_casca_visual.py
```

**Structure Decision**: Aplicação Flask existente; usar o cabeçalho e os cartões Jinja atuais. A folha de entrada já inclui `templates/` como fonte Tailwind. A interface não expõe API ou contrato externo novo, portanto não é necessário criar `contracts/`.

## Design and Validation

### Phase 0: Research

Decisões e evidências estão em [research.md](research.md). Não há incógnitas externas.

### Phase 1: Design

- Sem entidades ou mudanças no banco; ver [data-model.md](data-model.md).
- Validar os cenários e a inspeção visual em [quickstart.md](quickstart.md).
- Nenhuma alteração necessária à Constitution Check após o design.

## Complexity Tracking

Nenhuma violação da constituição ou nova dependência identificada.
