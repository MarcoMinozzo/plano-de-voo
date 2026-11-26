# Implementation Plan: Mapa interativo com carta e radar

**Branch**: `main` (branch de feature não criada) | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/009-mapa-interativo-carta-radar/spec.md`

## Summary

Adicionar controles no mapa existente para alternar ruas/carta visual e ligar/desligar radar, inicialmente desligado. Reorganizar METAR/TAF sem alterar os dados originais. A rota continua calculada e entregue pelo servidor. A carta WAC GeoPDF do AISWEB é somente candidata: primeiro validar a edição vigente, sua cobertura da rota, os termos de uso e um ambiente reproduzível de geração de tiles. Até todos os gates passarem, a carta permanece indisponível. Nenhum processamento cartográfico participa do cálculo do plano.

## Technical Context

**Language/Version**: Python 3.10+; Jinja, HTML, CSS e JavaScript existentes.

**Primary Dependencies**: Flask 3.0, requests 2.31, Leaflet 1.9 via CDN e Tailwind já configurado. Nenhuma dependência nova no runtime.

**Storage**: PostgreSQL; campos JSON existentes `carta`, `radar` e `meteorologia`. Ainda não definir armazenamento ou distribuição de tiles; isso depende da validação de direitos e infraestrutura. Nenhuma migração prevista nesta etapa.

**Testing**: pytest; `tests/test_tempo.py` e `tests/test_tela_piloto.py`. Testes de interface usam estados/camadas simulados; validação da fonte real é uma etapa manual com o PDF exato e ambiente autorizado.

**Target Platform**: Aplicação web Flask em navegadores móveis e desktop.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Aquisição ou conversão de carta nunca ocorre durante o cálculo da rota nem bloqueia a abertura do plano. Tiles só poderão ser produzidos após os gates e em processo separado.

**Constraints**: Preservar cálculos e geometria da rota do servidor; não inventar dados. Só usar edição oficial vigente, com georreferenciamento e cobertura validados para toda a rota, autorização documentada para os derivados e geração reproduzível. Não contornar o desafio Cloudflare, não usar a amostra de 2020 como carta vigente e não substituir a fonte sem nova decisão. O acesso ao plano respeita o piloto dono.

**Scale/Scope**: Um mapa por plano aberto, com pontos já calculados e metadados atuais de tempo, carta e radar. Sem persistência nova nesta etapa.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Estado | Evidência / salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | `spec.md`, plano e tarefas são criados antes de qualquer alteração observável. |
| II. Limite educacional | PASS | Manter aviso de que dados meteorológicos não autorizam voo nem substituem avaliação operacional. |
| III. Cálculo no servidor | PASS | A interface apenas desenha a rota existente; não calcula navegação. |
| IV. Unidades, fonte e indisponibilidade | PASS | Só exibir carta cuja edição, georreferenciamento e cobertura estejam comprovados; falhas e gates pendentes resultam em indisponibilidade explícita. |
| V. Pilha pequena e banco relacional | PASS | Reutilizar a pilha existente; sem conversão no runtime, dependência nova ou migração nesta etapa. Qualquer infraestrutura de tiles depende dos gates e de plano revisado. |
| Isolamento por piloto | PASS | Qualquer consulta futura a recursos do plano deve verificar que ele pertence ao piloto da sessão. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation (this feature)

```text
specs/009-mapa-interativo-carta-radar/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── camadas-do-mapa.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py                       # acesso autenticado ao plano; nenhuma rota WMS aprovada
servidor/
├── tempo.py                 # dados meteorológicos existentes; sem parser WMS aprovado
├── planos.py                # reutilizar consulta do plano por piloto; sem cálculo novo
└── modelos.py               # colunas JSON existentes; sem migração
templates/
└── plano.html               # controles, camadas e blocos METAR/TAF
tests/
├── test_tempo.py
└── test_tela_piloto.py
documentacao/
└── piloto.md
```

**Structure Decision**: Manter a aplicação Flask/Jinja existente. Nenhum endpoint WMS ou pipeline de conversão é aprovado neste plano. A interface e a integração da carta só avançam após os gates; qualquer armazenamento ou serviço de tiles requer plano revisado. A rota e o cálculo permanecem no servidor.

## Phase 0: Outline & Research

- Evidência e decisão atual registradas em [research.md](./research.md), com o histórico WMS marcado como substituído.
- O GeoPDF é apenas candidato, não fonte aprovada para exibição. Os quatro gates da decisão vigente são pré-requisitos para qualquer implementação de carta.
- A validação de gate não requer contornar o desafio Cloudflare; se o PDF atual ou os termos não puderem ser confirmados por meios autorizados, registrar o bloqueio e manter a carta indisponível.

## Phase 1: Design & Contracts

- Modelo de dados e estados em [data-model.md](./data-model.md); nenhuma mudança persistente prevista.
- Contrato de interação e dos estados em [contracts/camadas-do-mapa.md](./contracts/camadas-do-mapa.md); sem endpoint da carta antes dos gates.
- Validação manual e automatizada em [quickstart.md](./quickstart.md), incluindo os gates da fonte.
- Reavaliar Constituição: PASS; nenhum cálculo client-side, fallback enganoso, dado meteorológico inventado, conversão durante cálculo, migração ou dependência nova.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
