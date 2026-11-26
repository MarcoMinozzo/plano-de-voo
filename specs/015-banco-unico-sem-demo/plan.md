# Implementation Plan: Banco único e perfis sintéticos didáticos

**Branch**: `main` | **Date**: 2026-11-25 | **Spec**: [spec.md](spec.md)

## Summary

Usar uma única base de produto, mantendo `DATABASE_URL` como canônica e os
testes em banco separado. Importar os vinte proxies sintéticos existentes da
antiga base sem validar nem alterar seus valores, remover as dependências do
modo DEMO e manter avisos explícitos em seleção, cálculo e PDF.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: Flask, SQLAlchemy 2, psycopg 3, Alembic; sem novas dependências.

**Storage**: PostgreSQL 16 no produto; banco independente nos testes.

**Testing**: pytest; testes de migração com bancos descartáveis e sem conexão de produto.

**Target Platform**: Servidor Linux e ambiente local de desenvolvimento.

**Project Type**: Aplicação web Flask com interface e API JSON.

**Performance Goals**: Sem nova meta de latência; a mudança acrescenta somente vinte perfis.

**Constraints**: Preservar ROTAER/RAB do destino, os seis valores e unidades dos vinte proxies; não migrar pilotos, planos, perfis genéricos ou extrato RAB sintético; não alterar a base de origem; não pesquisar dados aeronáuticos; manter avisos didáticos e isolamento dos testes.

**Scale/Scope**: Uma base de produto, uma base legada somente como origem de importação e vinte perfis proxy.

## Constitution Check

- **Especificação antes do código**: atendido; esta feature tem spec, plano e terá tarefas antes de alterações de aplicação.
- **Limite educacional**: atendido; dados sintéticos terão rótulo explícito e aviso de não uso real.
- **Cálculo no servidor**: atendido; nenhum cálculo será movido ao navegador.
- **Unidades e fonte explícitas**: atendido pela exceção constitucional dos proxies, com unidades e identificação sintética, sem alegar validade para o modelo-alvo.
- **Banco e dependências**: atendido; um banco de produto, banco de teste isolado e nenhuma dependência nova.
- **Migração segura**: atendido; origem somente leitura, transação no destino e abortar em origem incompleta ou conflito divergente.

**Gate**: aprovado. Nenhuma violação constitucional ou decisão técnica pendente.

## Project Structure

### Documentation (this feature)

```text
specs/015-banco-unico-sem-demo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── aeronaves.md
│   └── importar-perfis-sinteticos.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py
alembic/env.py
servidor/
├── ambiente.py
├── catalogo.py
├── planos.py
├── proveniencia.py
├── pdf_plano.py
├── perfis_sinteticos.py
└── importar_perfis_sinteticos.py
templates/
├── plano_novo.html
└── plano.html
tests/
├── test_ambiente.py
├── test_perfis_sinteticos.py
├── test_importar_perfis_sinteticos.py
└── test_rota_pdf.py
documentacao/
├── operacao.md
└── piloto.md
```

**Structure Decision**: Aplicação web Flask existente, sem novos pacotes ou
serviços. Substituir os módulos ligados ao modo DEMO por um registro fixo de
identidade/rotulagem dos perfis e um comando de importação única. Não criar
uma nova semente: os valores devem vir exclusivamente dos vinte registros
existentes na base antiga.
