# Implementation Plan: Aumentar logo no login

**Branch**: `017-aumentar-logo-login` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/017-aumentar-logo-login/spec.md`

## Summary

Aumentar somente o logo dentro do cartão da página de entrar de 86,4 px para 103,68 px, mantendo proporção, posição, texto alternativo e comportamento do cabeçalho. Cadastro e páginas autenticadas permanecem inalterados.

## Technical Context

**Language/Version**: HTML/Jinja e CSS, aplicação Flask existente

**Primary Dependencies**: Tailwind CSS 4 já instalado; nenhuma dependência nova

**Storage**: N/A; não há alteração de dados

**Testing**: pytest focado em `tests/test_casca_visual.py`, compilação Tailwind e inspeção visual em navegador

**Target Platform**: Navegadores desktop e mobile

**Project Type**: Aplicação web Flask

**Performance Goals**: Sem impacto mensurável; reutiliza imagem local existente

**Constraints**: Alterar somente o tamanho do logo no login; preservar proporção, centralização, acessibilidade, cadastro, cabeçalho e formulário

**Scale/Scope**: Uma página pública e seu teste visual existente

## Constitution Check

- **Especificação antes do código**: PASS — especificação, plano e tarefas são preparados antes da implementação.
- **Limite educacional**: PASS — nenhum conteúdo ou resultado de voo é alterado.
- **Cálculo no servidor**: PASS — alteração exclusivamente visual.
- **Unidades e fonte explícitas**: PASS — não há grandeza aeronáutica nova.
- **Pilha pequena e banco relacional**: PASS — sem dependências, persistência ou migrações.
- **Acesso e segurança**: PASS — rotas, sessão e formulário não mudam.

## Project Structure

### Documentation (this feature)

```text
specs/017-aumentar-logo-login/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code

```text
templates/
├── entrar.html
└── cadastro.html
static/css/
├── input.css
└── tailwind.css
tests/
└── test_casca_visual.py
```

**Structure Decision**: Reutilizar os templates e a folha Tailwind existentes. A classe do logo de cadastro é a referência de comparação e não será alterada. Não há contrato de API nem modelo de dados nesta mudança.

## Design and Validation

### Phase 0: Research

Decisões e justificativa estão em [research.md](research.md). Não há incógnitas externas.

### Phase 1: Design

- Não há entidades nem mudança persistente; ver [data-model.md](data-model.md).
- Os passos de validação automatizada e visual estão em [quickstart.md](quickstart.md).
- A revisão pós-design da constituição não identificou violações.

## Complexity Tracking

Nenhuma violação da constituição ou nova dependência identificada.
