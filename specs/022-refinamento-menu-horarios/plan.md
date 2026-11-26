# Implementation Plan: Refinamento do menu e horários

**Branch**: `main` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/022-refinamento-menu-horarios/spec.md`

## Summary

Refinar o cabeçalho autenticado com logo maior, card central ajustado ao conteúdo, ícones e navegação sanduíche em telas estreitas. Harmonizar tons de texto/cartões e apresentar a hora de partida em minutos com “TL”, sem alterar o valor armazenado nem cálculos.

## Technical Context

**Language/Version**: HTML/Jinja e CSS; Python 3.10+ no servidor existente.

**Primary Dependencies**: Tailwind CSS e Flask/Jinja já instalados; nenhuma dependência nova.

**Storage**: Sem alteração de persistência.

**Testing**: Teste visual existente em `tests/test_casca_visual.py`, compilação Tailwind e inspeção manual em 390 px/1440 px.

**Target Platform**: Navegadores desktop e móveis.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Sem scripts, requisições ou dependências adicionais.

**Constraints**: Preservar URLs, saída POST, acessibilidade do botão sem rótulo visível e horário/calculações existentes; não introduzir overflow horizontal.

**Scale/Scope**: Cabeçalho autenticado compartilhado, painel de planos, tokens de cor e verificações visuais.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefa serão concluídos antes de editar templates/CSS. |
| II. Limite educacional | PASS | Nenhum aviso, cálculo ou conteúdo operacional será alterado. |
| III. Cálculo no servidor | PASS | O horário será apenas formatado na apresentação; cálculos continuam intocados. |
| IV. Unidades e fonte explícitas | PASS | Sem mudança em dados aeronáuticos ou suas fontes. |
| V. Pilha pequena e banco relacional | PASS | Sem dependências, tabelas ou migrações novas. |
| Segurança do acesso | PASS | Links existentes e saída por POST serão preservados; controles terão nome acessível. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation

```text
specs/022-refinamento-menu-horarios/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
templates/
├── base.html
└── painel.html
static/css/
├── input.css
└── tailwind.css
tests/
└── test_casca_visual.py
```

**Structure Decision**: Reutilizar o cabeçalho compartilhado e o painel atual. Usar markup sem dependências e os tokens CSS existentes, mantendo o CSS compilado sincronizado com a fonte.

## Phase 0: Outline & Research

As decisões de apresentação foram verificadas contra os padrões existentes e registradas em [research.md](./research.md). Não há incógnitas, integrações externas ou dependências novas.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md): confirma ausência de alterações em entidades e persistência.
- Não há contrato externo novo; links e endpoint de saída permanecem os existentes.
- [quickstart.md](./quickstart.md): define compilação, teste focado e conferência de viewports.
- Constituição reavaliada após o desenho: PASS.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
