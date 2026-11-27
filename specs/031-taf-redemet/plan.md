# Implementation Plan: Priorizar TAF da REDEMET

**Branch**: `031-taf-redemet` | **Date**: 2026-11-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/031-taf-redemet/spec.md`

## Summary

Priorizar o TAF mais recente fornecido pela REDEMET para cada indicativo da rota, preservando o AWC como fallback para o mesmo aeródromo. Reutilizar o JSON meteorológico existente; propagar a fonte real do TAF para a tabela de fontes e manter METAR e falhas independentes.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: Flask e `requests` existentes; sem dependências novas.

**Storage**: PostgreSQL existente; sem migração. O JSON meteorológico já guarda `taf`.

**Testing**: pytest focado em `tests/test_tempo.py`, `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py`.

**Target Platform**: Servidor Flask local e navegadores desktop/móveis.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Uma consulta REDEMET TAF por indicativo único na abertura ou montagem do plano; consultar AWC somente quando a REDEMET não entregar TAF utilizável.

**Constraints**: Chave REDEMET apenas no servidor; validar indicativo, mensagem, horários e estado HTTP; falha REDEMET deve preservar o fallback AWC sem afetar METAR. Não usar TAF de outro aeródromo.

**Scale/Scope**: Somente seleção, proveniência e exibição do TAF. Sem alterações de rota, cálculos, modelo de banco ou comportamento de METAR regional.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são criados antes de alterar código visível. |
| II. Limite educacional | PASS | Preservar o aviso didático existente; TAF não autoriza voo. |
| III. Cálculo no servidor | PASS | Consulta e seleção de fonte ficam no servidor. |
| IV. Fonte e indisponibilidade explícitas | PASS | Guardar fonte, emissão e validade publicadas; falha sem TAF válido permanece indisponível. |
| V. Pilha pequena e banco relacional | PASS | Reusar requests e JSON existente; nenhuma dependência ou migração. |
| TAF por aeródromo | PASS | REDEMET tem prioridade; AWC é fallback para o mesmo indicativo, sem fallback regional. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation

```text
specs/031-taf-redemet/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/taf-meteorologia.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
servidor/tempo.py
servidor/planos_consulta.py
templates/plano.html
servidor/pdf_plano.py
tests/test_tempo.py
tests/test_tela_piloto.py
tests/test_rota_pdf.py
```

**Structure Decision**: Estender o resolvedor de meteorologia em `servidor/tempo.py`, que já consulta AWC e percorre aeródromos distintos da rota. Usar `fonte` armazenada em cada observação TAF ao compor fontes; manter os consumidores HTML/PDF e o JSON atual compatíveis.

## Phase 0: Outline & Research

- Decisão e evidências da API oficial REDEMET estão em [research.md](./research.md).
- O endpoint oficial aceita um ou mais indicativos ICAO e retorna JSON com mensagem, localidade, recebimento e validade.
- Selecionar a mensagem válida mais recente para o mesmo indicativo, ordenando por recebimento; se não houver uma utilizável, recorrer ao AWC.
- A consulta GET do detalhe já atualiza meteorologia sem persistir. A geração/edição do plano persiste o snapshot existente.

## Phase 1: Design & Contracts

- A entidade TAF existente ganha metadados de fonte e validade; sem migração. Ver [data-model.md](./data-model.md).
- O contrato de seleção e de fallback está em [contracts/taf-meteorologia.md](./contracts/taf-meteorologia.md).
- Cenários de teste e validação estão em [quickstart.md](./quickstart.md).
- Revalidar que chave não aparece em HTML/JSON/logs, o TAF permanece ligado ao ICAO correto e erro TAF não oculta METAR.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
