# Implementation Plan: Redesenho da página do plano

**Branch**: `027-redesenhar-pagina-plano` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/027-redesenhar-pagina-plano/spec.md`

## Summary

Reorganizar a página de detalhes em um card principal com aproximadamente 80% da largura em telas largas, rota completa, dados oficiais dos aeródromos, alertas evidentes e mapa mais legível. Reutilizar Flask/Jinja, Leaflet e Tailwind. Ampliar a carga ROTAER para persistir contatos somente quando publicados, com campos opcionais. Remover a máscara de cobertura RainViewer do desenho sobre o mapa; manter o aviso conciso de cobertura, crédito e horário quando a camada estiver ativa. Google Maps permanece desativado sem chave.

## Technical Context

**Language/Version**: Python 3.10+; Jinja, HTML, CSS e JavaScript existentes.

**Primary Dependencies**: Flask, SQLAlchemy 2, Alembic, requests, Leaflet 1.9 e Tailwind existente; nenhuma dependência nova.

**Storage**: PostgreSQL. Adicionar campos opcionais de telefone e e-mail à entidade `Aerodromo`; migração aditiva e valores sincronizados somente com dados AISWEB/ROTAER publicados.

**Testing**: pytest focado em `tests/test_tela_piloto.py`, `tests/test_tempo.py`, `tests/test_catalogo_aerodromos.py` e migrações existentes.

**Target Platform**: Aplicação Flask em navegadores móveis e desktop.

**Project Type**: Aplicação web server-rendered.

**Performance Goals**: Não adicionar chamadas externas ao abrir um plano. Contatos vêm do catálogo já carregado; RainViewer continua sendo consultado somente após ativação explícita.

**Constraints**: Não alterar cálculo, propriedade do plano, geometria da rota ou PDF. Não inventar contato. Manter REDEMET oficial separado de RainViewer; manter carta AISWEB indisponível até passar os gates existentes. Não mostrar ruas como carta. Chaves permanecem fora do repositório.

**Scale/Scope**: `app.py`, `servidor/modelos.py`, `servidor/rotaer_parse.py`, fluxo de importação ROTAER, migração Alembic, `templates/plano.html`, testes e `documentacao/piloto.md`.

## Constitution Check

| Princípio | Estado | Evidência / salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec 027, plano e tarefas antecedem mudanças observáveis. |
| II. Limite educacional | PASS | O aviso geral didático e de não autorização de voo permanece visível; o PDF fica inalterado. |
| III. Cálculo no servidor | PASS | A interface apenas organiza dados e desenha camadas; rota e limites continuam no servidor. |
| IV. Unidades, fontes e indisponibilidade | PASS | Dados aeroportuários vêm do ROTAER; contatos ausentes são indisponíveis. WAC continua indisponível sem validação. REDEMET e RainViewer mantêm identidade e estados distintos. |
| V. Pilha e banco relacional | PASS | PostgreSQL, SQLAlchemy e Alembic existentes; migração aditiva e sem dependência nova. |
| Acesso e isolamento | PASS | A rota da página continua autorizada pelo piloto dono; nenhuma nova rota pública será criada. |

**Recheck após Phase 1**: PASS. A alteração de schema é limitada a contatos oficiais opcionais; não cria fonte secundária, não mistura radares e não substitui a WAC.

## Project Structure

### Documentation

```text
specs/027-redesenhar-pagina-plano/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── plano-detalhes.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
app.py                              # passar aeródromos já resolvidos ao template
servidor/modelos.py                 # campos de contato opcionais em Aerodromo
servidor/rotaer_parse.py            # interpretar somente contato publicado
servidor/catalogo.py                # sincronizar campos da emenda oficial
alembic/versions/                   # migração aditiva nullable
templates/plano.html                # card, dados, alertas e controles do mapa
static/css/tailwind.css              # classes compiladas para o novo layout
tests/test_tela_piloto.py           # saída da página, controles e responsividade
tests/test_catalogo_aerodromos.py   # parsing e atualização de contato
tests/test_tempo.py                 # limites/estado dos radares
documentacao/piloto.md              # controles e avisos da página
```

**Structure Decision**: Manter o fluxo server-rendered atual. `app.py` já resolve os aeródromos da rota; o template recebe os registros para mostrar dados, sem replicar cálculos. O pedido explícito de 80% da viewport em telas largas prevalece sobre o limite de 48 rem documentado no desenho anterior; o restante do branding continua igual.

## Phase 0: Outline & Research

- [research.md](./research.md) registra os campos disponíveis, as limitações atuais do parser e o diagnóstico visual das camadas.
- Decisão de contato: guardar telefone/e-mail somente se AISWEB/ROTAER os publicar; no refresh da emenda, ausências limpam valores antigos para não manter contato obsoleto.
- Decisão de mapa: ruas são a base inicial; Google é desativado sem chave; REDEMET e RainViewer continuam controles independentes. Não desenhar a máscara RainViewer que atualmente obscurece grandes áreas da base.
- Nenhum novo serviço externo ou pacote será adicionado.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) descreve aeródromos, contatos opcionais, validação e sincronização.
- [contracts/plano-detalhes.md](./contracts/plano-detalhes.md) define conteúdo, estados e interação da página.
- [quickstart.md](./quickstart.md) define compilação Tailwind, testes automatizados e inspeção visual em 390 px/1440 px.
- Pós-design Constitution Check: PASS. Aviso didático, origem dos dados e indisponibilidade exigida continuam presentes; impressão superior e PDF permanecem.

## Complexity Tracking

| Decisão | Custo | Justificativa |
|---|---|---|
| Migração aditiva para contatos opcionais | Baixo | Necessária para exibir somente dados publicados e atualizáveis do ROTAER sem chamadas ao abrir cada plano. |
