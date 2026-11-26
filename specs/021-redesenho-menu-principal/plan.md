# Implementation Plan: Redesenho do menu principal

**Branch**: `main` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/021-redesenho-menu-principal/spec.md`

## Summary

Reorganizar a navegação autenticada como um card azul semitransparente, com logo maior fora dele e ações globais em maiúsculas. Mover a impressão do voo da navegação global para o card de resumo do plano individual, preservando links e envio do formulário de saída.

## Technical Context

**Language/Version**: HTML/Jinja e CSS; aplicação Flask em Python 3.10+.

**Primary Dependencies**: Tailwind CSS já instalado; nenhuma dependência nova.

**Storage**: Sem alteração de dados ou persistência.

**Testing**: pytest focado em `tests/test_casca_visual.py` e regressões relacionadas à navegação e PDF.

**Target Platform**: Navegadores desktop e móveis.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Nenhum script ou request adicional.

**Constraints**: Preservar URLs, POST de saída, funcionamento do PDF, conteúdo do cabeçalho público e ausência de overflow horizontal; manter o menu em 70% da viewport e permitir quebra de itens em telas estreitas.

**Scale/Scope**: Cabeçalho autenticado compartilhado, card de resumo do plano individual, CSS Tailwind compilado e testes visuais.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas precedem as alterações em templates e CSS. |
| II. Limite educacional | PASS | Avisos didáticos do plano permanecem intactos. |
| III. Cálculo no servidor | PASS | Nenhuma fórmula ou comportamento de domínio é movido ao cliente. |
| IV. Unidades e fonte explícitas | PASS | Conteúdo técnico do plano não é alterado. |
| V. Pilha pequena e banco relacional | PASS | Nenhuma dependência, banco ou migração nova. |
| Segurança do acesso | PASS | A ação “SAIR” preserva POST e o endpoint existente. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation (this feature)

```text
specs/021-redesenho-menu-principal/
├── plan.md
├── research.md
├── data-model.md
├── contracts/menu-principal.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
templates/
├── base.html
└── plano.html
static/css/
├── input.css
└── tailwind.css
tests/
└── test_casca_visual.py
```

**Structure Decision**: Reutilizar o cabeçalho compartilhado e o card `#resumo`; manter os estilos na fonte Tailwind existente e validar o HTML renderizado pelo cliente Flask.

## Phase 0: Outline & Research

Decisões de cor, dimensões, posicionamento e adaptação estreita estão registradas em [research.md](./research.md). Não há integração externa ou incógnita que exija pesquisa externa.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md): confirma ausência de dados e estados novos.
- [contracts/menu-principal.md](./contracts/menu-principal.md): define os itens, a colocação da impressão e a preservação das ações.
- [quickstart.md](./quickstart.md): registra a validação automatizada e de viewports.
- Constituição reavaliada após o desenho: PASS; mudança restrita à apresentação e aos pontos de navegação existentes.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
