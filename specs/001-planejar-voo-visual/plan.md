# Implementation Plan: Planejar voo visual

**Branch**: `001-planejar-voo-visual` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-planejar-voo-visual/spec.md`

## Summary

O piloto entra num espaço só dele, informa origem, destino e hora, e recebe um plano de voo visual de avião pequeno. O primeiro manual é o do Cessna 140. Dados técnicos saem desse manual no PostgreSQL. Dados particulares deste voo são digitados pelo piloto. O servidor calcula navegação, combustível e limites, busca tempo, carta, radar e vento, sugere o checklist e gera o PDF. O que a fonte não entregar fica indisponível.

A abordagem técnica está em [research.md](./research.md): Flask, PostgreSQL 16, SQLAlchemy 2, psycopg 3, Alembic, sessão Flask e hash do Werkzeug.

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: Flask 3.0.0, SQLAlchemy 2, psycopg 3, Alembic, requests 2.31.0, reportlab 4.0.7, Werkzeug (já vem com o Flask), Leaflet 1.9 pelo CDN

**Storage**: PostgreSQL 16. Um registro de manual, aeródromos, pilotos e planos. Boletim, vento, carta e radar em JSON no plano.

**Testing**: pytest para cálculo, limite do manual, isolamento entre pilotos, senha curta, bloqueio após cinco recusas e sessão encerrada. Conferência manual no navegador em [quickstart.md](./quickstart.md)

**Target Platform**: Servidor Linux local, navegador em português

**Project Type**: Aplicação web Flask, página no servidor, mapa no navegador

**Performance Goals**: Com manual e fontes disponíveis, o piloto conclui da origem ao PDF em até 15 minutos. Cada chamada externa espera no máximo 8 segundos e, se falhar, marca o item como indisponível.

**Constraints**: Sem segundo fator. Senha com no mínimo 8 caracteres. Cinco recusas em 15 minutos bloqueiam a identificação por 15 minutos, com a mesma mensagem de identificação inexistente. Sessão encerra ao sair e após 8 horas sem uso. Cookie HttpOnly, SameSite=Lax e Secure fora de acesso local. Sem protocolo do plano em autoridade. Sem fórmula no JavaScript. Sem segunda cópia dos números do manual. Chaves da REDEMET e do AISWEB fora do repositório. Texto e PDF em português. Aviso de que o resultado não autoriza o voo. Orientação do piloto em `documentacao/piloto.md`. Operação em `documentacao/operacao.md`, sem segredo.

**Scale/Scope**: Dezenas de pilotos, um espaço cada. Uma aeronave com manual na primeira entrega (Cessna 140). Sete aeródromos na semente, e outros indicativos quando tiverem coordenada e fonte.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição 2.1.1. O nome do projeto é Plano de voo.

| Portão | Antes da pesquisa | Depois do desenho |
| --- | --- | --- |
| Spec antes de código de produto | Passa. Este plano não altera `app.py`. | Passa. Artefatos só em `specs/001-planejar-voo-visual/`. |
| Limite educacional e sem protocolo | Passa. PDF e tela incluem o aviso. | Passa. O contrato do PDF exige o aviso. |
| Cálculo no servidor | Passa. | Passa. Leaflet só desenha rota e radar. |
| Unidade, fonte e falha visível | Passa. | Passa. O modelo guarda unidade, fonte e o estado indisponível. |
| PostgreSQL, pilha nomeada, chave fora do repositório | Passa. | Passa. Ver [research.md](./research.md) e [data-model.md](./data-model.md). |
| Plano só do piloto da sessão | Passa. | Passa. Toda leitura filtra `piloto_id`. |
| Senha, bloqueio e sessão | Passa. Regras na constituição 2.1.1. | Passa. Ver contrato de sessão. |
| Documentação do piloto e de operação, sem segredo | Passa. | Passa. Textos em `documentacao/`. |

Nenhum portão falhou. Não há violação a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/001-planejar-voo-visual/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-plano.md
└── tasks.md              # ainda não existe; sai em /speckit-tasks
```

### Source Code (repository root)

```text
app.py                      # entrada Flask atual; passa a montar o aplicativo
servidor/
├── modelos.py              # tabelas PostgreSQL
├── auth.py                 # cadastro, entrada, sessão
├── calculo.py              # navegação, combustível, limites, efeito do vento
├── tempo.py                # METAR, TAF, radar, carta, vento de área
├── planos.py               # criar, listar, editar, apagar, checklist
└── pdf_plano.py            # PDF do plano
templates/                  # páginas em português
documentacao/
├── piloto.md               # texto da tela e do PDF
└── operacao.md             # subir o sistema, sem segredos
static/
tests/
├── test_calculo.py
└── test_isolamento.py
alembic/                    # migrações
```

**Structure Decision**: Continua uma aplicação Flask, com página servida pelo servidor. O cálculo sai de um único `app.py` e vai para `servidor/`, que é o que a constituição 2.0.0 exige. O navegador não ganha framework. O arquivo `cessna140.db` deixa de ser o banco do produto.

## Complexity Tracking

Nenhuma violação da constituição. A troca de SQLite por PostgreSQL e as dependências SQLAlchemy, psycopg e Alembic estão nomeadas na constituição 2.0.0 e justificadas em [research.md](./research.md).
