# Implementation Plan: Rota com escalas

**Branch**: `002-rota-com-escalas` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-rota-com-escalas/spec.md`

## Summary

O piloto continua informando origem, destino e hora. O servidor passa a escolher a rota e as escalas. Origem, destino e escala saem dos aeródromos de avião da emenda vigente do ROTAER. O avião sai do catálogo de modelos pequenos do Registro Aeronáutico Brasileiro, e o número técnico só entra com o manual oficial. A conta permanece no servidor, no processo Flask já usado pelo plano direto.

A abordagem está em [research.md](./research.md). Não há biblioteca nova.

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: As já nomeadas na constituição 2.2.0: Flask 3.0.0, SQLAlchemy 2, psycopg 3, Alembic, requests 2.31.0, reportlab 4.0.7, Leaflet 1.9 pelo CDN. Nenhuma dependência nova.

**Storage**: PostgreSQL 16. Aeródromo passa a guardar a emenda e o tipo publicado. Modelo de avião guarda a frota e o estado do manual. A rota do plano é uma lista ordenada de trechos.

**Testing**: pytest, com publicação e registro fictícios pequenos nos testes. A carga nacional real não entra no teste automático.

**Target Platform**: O mesmo processo Flask local do plano direto.

**Project Type**: Aplicação web de um processo, páginas servidas pelo servidor.

**Performance Goals**: Montar a rota de um par de aeródromos brasileiros em tempo de uma interação de formulário, sem varrer trechos mais longos do que o alcance de planejamento do manual.

**Constraints**: Sem número de manual inventado. Sem coordenada inventada. Sem vento de cauda quando o vento oficial não cobre o trecho. Sem fórmula no JavaScript. Chave do AISWEB fora do repositório. Texto em português. O resultado não autoriza o voo.

**Scale/Scope**: A emenda vigente do ROTAER para aeródromos de avião, e os modelos de avião pequeno do extrato público do RAB. Um plano continua de um piloto.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição 2.2.0. O nome do projeto é Plano de voo.

| Portão | Antes da pesquisa | Depois do desenho |
| --- | --- | --- |
| Spec antes do código | Passa. Este plano não altera o servidor. | Passa. Artefatos em `specs/002-rota-com-escalas/`. |
| Cálculo no servidor | Passa. A rota e as escalas ficam no servidor. | Passa. O mapa só desenha trechos já calculados. |
| Unidade, fonte e falha visível | Passa. | Passa. Emenda, manual, vento e pôr do sol têm estado indisponível. |
| Catálogo só da emenda vigente | Passa. | Passa. Sem chave ou sem emenda, o catálogo nacional fica indisponível. |
| Número só do manual | Passa. O corte de 80% não autoriza número emprestado. | Passa. Modelo sem manual não calcula. |
| Plano só do piloto da sessão | Passa. Reusa a sessão do plano direto. | Passa. |
| Nenhuma dependência nova | Passa. `requests` já busca o AISWEB. | Passa. |

## Project Structure

### Documentation (this feature)

```text
specs/002-rota-com-escalas/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/api-rota.md
└── tasks.md
```

### Source Code (repository root)

```text
servidor/
├── catalogo.py             # ROTAER vigente e extrato do RAB
├── rota.py                 # escolha da rota e das escalas
├── calculo.py              # trecho, já existente, passa a ser chamado por perna
├── planos.py               # grava a rota no plano
└── pdf_plano.py            # imprime os trechos

templates/plano.html        # lista os trechos e desenha a linha já calculada
templates/plano_novo.html   # origem e destino no catálogo; não pede a escala
documentacao/piloto.md      # o que é escala, catálogo indisponível e modelo sem manual
```

**Structure Decision**: Continua o processo Flask do plano direto. Catálogo e rota entram em módulos novos. O navegador não ganha framework nem fórmula.

## Complexity Tracking

Nenhuma violação da constituição. A carga do ROTAER e do RAB usa o `requests` já justificado. Não entra biblioteca de grafo.
