# Implementation Plan: Proxies de aeronaves DEMO

**Branch**: `007-proxies-aeronaves-demo` | **Date**: 2026-11-24 | **Spec**: [spec.md](./spec.md)

**Input**: Especificação da feature em `specs/007-proxies-aeronaves-demo/spec.md`

## Summary

Completar o catálogo de demonstração com até 20 perfis proxy sintéticos e preservar os 20 perfis genéricos existentes. O formulário de novo plano oferecerá somente os proxies, pelo nome do modelo-alvo, com um aviso DEMO geral; os perfis genéricos permanecem armazenados, mas não são selecionáveis. Cada valor usado nos cálculos terá limites admissíveis, fontes aplicáveis, método e versão de geração e incerteza registrados. O DEMO receberá a emenda vigente e os aeródromos oficiais já carregados no banco normal, por transferência de provisionamento restrita a essas tabelas; a aplicação DEMO não consultará a base normal nem dependerá do API AISWEB para essa carga.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: Flask, SQLAlchemy 2, Alembic; sem novas dependências  
**Storage**: PostgreSQL 16; banco normal e banco DEMO distintos  
**Testing**: pytest, fixtures e fontes meteorológicas simuladas  
**Target Platform**: Aplicação web local de desenvolvimento  
**Project Type**: Serviço web Flask  
**Performance Goals**: Catálogo DEMO mantém até 40 perfis; a seleção do plano oferece até 20 proxies pelo nome-alvo, sem alterar o catálogo normal  
**Constraints**: Não sintetizar meteorologia, vento, carta ou dados de aeródromo; não expor proxies no modo normal; preservar os planos e dados já existentes; falhas de configuração/fonte devem continuar explícitas  
**Scale/Scope**: 20 perfis genéricos existentes, até 20 proxies, emenda ROTAER vigente e até 4.519 aeródromos da base normal

## Constitution Check

- **Spec-first**: aprovado em [spec.md](./spec.md); esta implementação segue seus critérios de aceitação.
- **Uso educacional**: os perfis e qualquer resultado do DEMO serão identificados como sintéticos e não operacionais na seleção, resultado e PDF.
- **Proveniência**: cada campo técnico sintético exige intervalo aplicável, referência(s), método, versão da semente e incerteza; perfil sem evidência suficiente não será selecionável.
- **Integridade dos cálculos**: validar unidades, limites e relações físicas; velocidade e consumo devem representar o mesmo perfil de cruzeiro.
- **Isolamento**: aplicação, migrações e semente DEMO usam exclusivamente `DATABASE_URL_DEMO`; a transferência do ROTAER é uma operação explícita de provisionamento, limitada a dados oficiais e sem acesso da aplicação DEMO à base normal em runtime.
- **Meteorologia e aeródromos**: usar somente dados oficiais; indisponibilidade das fontes deve ser apresentada como indisponibilidade, sem fallback sintético.
- **Compatibilidade**: catálogo normal segue limitado a 30 modelos e não aceita dados sintéticos; não introduzir dependências.

## Project Structure

### Documentação desta feature

```text
specs/007-proxies-aeronaves-demo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── catalogo-demo.md
└── tasks.md
```

### Código existente a alterar

```text
servidor/
├── modelos.py                 # metadados para faixas e geração sintética
├── proveniencia.py            # validação por campo e formatação da procedência
├── catalogo.py                # limite 30 normal / 40 DEMO e filtro de elegibilidade
├── semente_demo.py            # atualizar 20 genéricos e inserir os proxies
└── planos.py                  # preservar snapshot e restrições do cálculo DEMO

servidor/importar_rotaer_demo.py # provisionar somente ROTAER oficial normal -> DEMO
app.py                         # seleção/resultado com rótulos e procedência
templates/                     # seleção compacta; procedência completa no resultado e no PDF
tests/                         # testes de validação, catálogo e fluxo de plano
documentacao/operacao.md       # provisionamento oficial do ROTAER e DEMO
```

**Structure Decision**: manter a implementação dentro do serviço Flask e dos testes existentes; usar um comando explícito, fora do runtime web, para transferir a lista oficial já disponível sem copiar dados de usuário.

## Complexity Tracking

Não há exceções à constituição. O provisionamento separado é necessário para manter o isolamento de runtime e evitar uma chamada AISWEB redundante.
