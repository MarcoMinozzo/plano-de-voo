# Implementation Plan: Capa e diagramação do PDF de voo

**Branch**: `main` (working tree preservada) | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/011-capa-e-diagramacao-pdf/spec.md`

## Summary

Adicionar nome de exibição ao perfil do piloto, com backfill para contas
existentes e edição autenticada. Reestruturar o PDF atual em capa e relatório
técnico paginado, usando o emblema e as cores existentes. Preservar todos os
dados, fontes, avisos e conteúdo obrigatório; não alterar cálculos nem a
restrição de acesso ao plano.

## Technical Context

**Language/Version**: Python 3.10+; Jinja, HTML e CSS existentes.

**Primary Dependencies**: Flask 3.0, SQLAlchemy 2, Alembic e ReportLab 4.0.7,
já instalados; nenhuma dependência nova.

**Storage**: PostgreSQL existente. Adicionar `piloto.nome_exibicao`, requerido
e limitado a 160 caracteres; migração faz backfill a partir de
`piloto.identificacao`.

**Testing**: pytest; ampliar `tests/test_acesso.py`, `tests/test_casca_visual.py`
e `tests/test_rota_pdf.py`; simular fluxo de cadastro e perfil sem chamadas
externas.

**Target Platform**: Servidor Flask e leitores/impressoras de PDF A4.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: PDF gerado em memória e entregue sem persistir arquivo;
paginação não deve depender do tamanho fixo de uma linha.

**Constraints**: Preservar os dados e avisos atuais; não modificar o checklist
persistido; manter PDF apenas para piloto dono do plano. Perfil só pode alterar
o próprio nome. Migração deve partir da revisão única `d1e2f3a4b5c6`; backfill
preserva credenciais. O aviso educacional, procedência e texto completo de
`documentacao/piloto.md` permanecem no PDF.

**Scale/Scope**: Uma coluna de perfil, cadastro/edição do nome e redesenho do
relatório PDF. Sem mudança nos cálculos ou no conteúdo salvo dos planos.

## Constitution Check

| Princípio | Estado | Evidência / salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são preparados antes do runtime. |
| II. Limite educacional | PASS | Avisos, estimativas e estados DEMO permanecem visíveis no PDF. |
| III. Cálculo no servidor | PASS | Perfil e PDF continuam montados no servidor; nenhuma fórmula no cliente. |
| IV. Unidades e fonte explícitas | PASS | Relatório preserva unidades, fontes, datas e indisponibilidades atuais. |
| V. Banco relacional e pilha pequena | PASS | Coluna PostgreSQL via Alembic; reutiliza ReportLab, sem dependência nova. |
| Acesso por piloto | PASS | Edição restrita ao usuário da sessão; PDF mantém verificação do dono. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation (this feature)

```text
specs/011-capa-e-diagramacao-pdf/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── perfil-e-pdf.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
servidor/modelos.py             # nome de exibição
servidor/auth.py                # validação de nome no cadastro
app.py                          # edição de perfil e PDF autenticados
templates/cadastro.html         # nome no cadastro
templates/base.html             # navegação de perfil
templates/perfil.html           # edição do próprio nome
servidor/pdf_plano.py           # capa e relatório paginado
alembic/versions/               # backfill de contas existentes
tests/test_acesso.py            # cadastro e edição do perfil
tests/test_casca_visual.py      # navegação e acesso
tests/test_rota_pdf.py          # capa, conteúdo e paginação
```

**Structure Decision**: Reutilizar o monólito Flask, o perfil `Piloto`, as
rotas/templates existentes e ReportLab. A edição do nome usa uma nova tela
protegida pelo mesmo padrão de sessão; o PDF recebe o nome do piloto
autenticado cuja propriedade do plano já foi validada.

## Phase 0: Outline & Research

- [research.md](./research.md) confirma o gerador PDF atual, o emblema aprovado,
  a única revisão Alembic vigente e as decisões de migração/layout.
- Manter geração em memória; usar os recursos de texto, tabelas, imagens e
  paginação da biblioteca já instalada.
- Migração não remove dados: preenche `nome_exibicao` legado com
  `identificacao`. Um downgrade posterior removeria nomes editados.
- Não há incerteza técnica que exija pesquisa externa.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) define o campo, validação e backfill.
- [contracts/perfil-e-pdf.md](./contracts/perfil-e-pdf.md) registra cadastro,
  edição protegida e saída do PDF.
- [quickstart.md](./quickstart.md) orienta testes e verificação manual A4.
- Reavaliação da constituição: PASS. A mudança mantém o cálculo no servidor,
  o limite educacional, as fontes, o isolamento entre pilotos e a stack aprovada.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
