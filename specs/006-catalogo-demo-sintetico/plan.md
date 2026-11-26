# Implementation Plan: Catálogo sintético isolado para DEMO

**Branch**: `006-catalogo-demo-sintetico` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-catalogo-demo-sintetico/spec.md`

## Summary

Adicionar modo DEMO explicitamente opt-in que usa exclusivamente um PostgreSQL separado, bloqueia inicialização fora do ambiente de desenvolvimento e permite vinte perfis fictícios sem torná-los elegíveis no modo normal. A procedência sintética será explícita e não terá data editorial inventada. Rotas DEMO dependem de uma emenda ROTAER oficial vigente carregada no próprio banco DEMO; nenhum dado de navegação ou condição de voo será sintetizado.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: Flask 3.0.0, SQLAlchemy 2, psycopg 3, Alembic  
**Storage**: PostgreSQL 16; banco DEMO separado do banco normal  
**Testing**: pytest; testes unitários de configuração/proveniência e testes de integração existentes  
**Target Platform**: Serviço web Flask executado localmente em desenvolvimento  
**Project Type**: Aplicação web monolítica Flask  
**Performance Goals**: Sem nova meta de desempenho; o catálogo contém vinte perfis  
**Constraints**: Sem dependências novas; sem fallback de banco; sem modificar coordenadas, vento, meteorologia, carta ou pôr do sol; sem fórmula no navegador  
**Scale/Scope**: Uma configuração de ambiente, uma semente isolada de vinte aeronaves, catálogo, cálculo, telas e PDF

## Constitution Check

- **Especificação antes do código**: atendido; esta feature tem spec, plano e terá tarefas em `specs/006-catalogo-demo-sintetico/`.
- **Limite educacional**: atendido; DEMO sempre é identificado e permanece não operacional.
- **Cálculo no servidor**: atendido; somente o servidor recebe os perfis sintéticos para cálculo.
- **Unidades e procedência**: atendido com tipo de procedência `sintetica`, valores unitados e sem simular data editorial.
- **PostgreSQL e migrações**: atendido; sem banco adicional além de PostgreSQL, usando Alembic e sem nova dependência.
- **Catálogo ROTAER**: atendido; planos DEMO exigem emenda oficial vigente no banco DEMO; nenhuma semente local serve como substituta.
- **Segregação de produção**: atendido por modo opt-in, ambiente de desenvolvimento obrigatório, URL DEMO exclusiva e filtro sintético desativado por padrão.

**Post-design check**: O banco DEMO continua PostgreSQL; o helper escolhe a URL antes de abrir conexão; o modo normal mantém os filtros atuais; dados de navegação continuam provenientes do ROTAER oficial. A extensão do tipo de procedência não altera os requisitos de data editorial para fontes oficiais ou secundárias. Sem violações conhecidas.

## Project Structure

### Documentation (this feature)

```text
specs/006-catalogo-demo-sintetico/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── catalogo-aeronaves.md
└── tasks.md
```

### Source Code

```text
app.py
servidor/
├── ambiente.py                 # Seleção e validação do modo e da URL
├── catalogo.py                 # Carga oficial ROTAER/RAB no banco selecionado
├── catalogo_rab.py
├── modelos.py
├── planos.py
├── proveniencia.py
├── semente_demo.py             # Perfis sintéticos, somente no banco DEMO
└── pdf_plano.py
alembic/
└── versions/                   # Migração da fonte sintética
templates/
├── plano_novo.html
└── plano.html
tests/
├── test_ambiente_demo.py
├── test_catalogo_aeronaves.py
├── test_tela_piloto.py
└── test_rota_pdf.py
documentacao/
├── operacao.md
└── piloto.md
```

**Structure Decision**: Manter a aplicação Flask monolítica existente. Concentrar resolução de ambiente em um helper reutilizável pelos comandos da aplicação, Alembic e catálogo; manter a carga DEMO em módulo separado da semente normal.

## Complexity Tracking

Não há violações da constituição nem dependências adicionais.
