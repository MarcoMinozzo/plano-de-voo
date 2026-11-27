# Implementation Plan: Apresentação legível de METAR e TAF

**Branch**: `032-metar-taf-display` | **Date**: 2026-11-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/032-metar-taf-display/spec.md`

## Summary

Preservar os boletins METAR e TAF originais em blocos visuais de terminal e adicionar leituras tabulares por aeródromo. Expandir a interpretação existente de METAR e criar uma leitura determinística dos grupos TAF no servidor, incluindo explicações internas para códigos meteorológicos conhecidos e indicação explícita dos desconhecidos.

## Technical Context

**Language/Version**: Python 3.10+; Jinja2 nos templates existentes.

**Primary Dependencies**: Flask, requests e Tailwind CSS existentes; sem dependências novas.

**Storage**: PostgreSQL existente; leituras são derivadas por requisição, sem migração ou persistência.

**Testing**: pytest focado em `tests/test_tempo.py` e `tests/test_tela_piloto.py`; `npm run css:build`.

**Target Platform**: Servidor Flask e navegadores desktop/móveis.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Interpretar cada boletim uma vez por requisição, sem chamadas externas ou aumento das consultas meteorológicas.

**Constraints**: Preservar literalmente o boletim original; não inferir campos ausentes; manter fonte/unidades/horários e indisponibilidade atuais; associar condições TAF ao grupo temporal correto; manter o parser e tradutor no servidor.

**Scale/Scope**: Somente a exibição na página de detalhes do plano. Não alterar consulta meteorológica, PDF, rota, cálculos ou persistência.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são criados antes de editar servidor, template ou CSS. |
| II. Limite educacional | PASS | Preservar o aviso de uso exclusivamente didático e não operacional. |
| III. Cálculo e meteorologia no servidor | PASS | Extração e tradução são feitas no servidor; o template apenas apresenta. |
| IV. Fonte e indisponibilidade explícitas | PASS | Manter texto original, fonte/horário/unidades existentes e marcar campos desconhecidos sem inventar interpretação. |
| V. Pilha pequena | PASS | Reusar Python/Jinja/Tailwind existentes; nenhuma dependência ou migração. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation

```text
specs/032-metar-taf-display/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/meteorologia-ui.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
app.py
servidor/tempo.py
templates/plano.html
static/css/input.css
static/css/tailwind.css
tests/test_tempo.py
tests/test_tela_piloto.py
```

**Structure Decision**: Reusar `campos_metar` e o enriquecimento de `boletins_por_aerodromo` em `app.py`. Adicionar o parser TAF e o catálogo de fenômenos em `servidor/tempo.py`; apresentar os dados já interpretados em `templates/plano.html`. Classes de apresentação seguem Tailwind e CSS compilado existentes.

## Phase 0: Outline & Research

- Padrões atuais e convenções de grupos/códigos meteorológicos estão em [research.md](./research.md).
- O METAR já tem campos estruturados e tabela em português; fenômenos ainda aparecem só como código.
- O TAF só aparece como texto bruto; seu parser deve formar grupos base e de mudança, mantendo períodos e campos associados.
- A leitura será transitória e calculada no servidor; códigos desconhecidos ficam visíveis sem tradução inventada.

## Phase 1: Design & Contracts

- Nenhuma entidade persistida ou migração: as estruturas tabulares são projeções temporárias. Ver [data-model.md](./data-model.md).
- O contrato interno de leitura e apresentação está em [contracts/meteorologia-ui.md](./contracts/meteorologia-ui.md).
- Cenários de teste e validação visual móvel estão em [quickstart.md](./quickstart.md).
- Compilar Tailwind depois de atualizar o template e validar em viewport de 390 px.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
