# Implementation Plan: Rota com escalas

**Branch**: `002-rota-com-escalas` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-rota-com-escalas/spec.md`

## Summary

O piloto continua informando origem, destino e hora. O servidor passa a escolher a rota e as escalas. Origem, destino e escala saem dos aeródromos de avião da emenda vigente do ROTAER. O avião sai do catálogo de modelos pequenos do Registro Aeronáutico Brasileiro, e o número técnico só entra com o manual oficial. A conta permanece no servidor, no processo Flask já usado pelo plano direto.

A abordagem está em [research.md](./research.md). Não há biblioteca nova.

**Revisão de 2026-11-24**: a clarificação dessa data troca a meta de 80% da frota pelos 20 modelos de maior frota com manual oficial. Cada manual entra num arquivo por modelo em `servidor/manuais/`, com valor, unidade, documento e página de cada número. O comando `python -m servidor.manuais` valida esses arquivos e grava o modelo no PostgreSQL como `gravado`. O registro está em [contracts/registro-manual.md](./contracts/registro-manual.md).

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: As já nomeadas na constituição 2.2.0: Flask 3.0.0, SQLAlchemy 2, psycopg 3, Alembic, requests 2.31.0, reportlab 4.0.7, Leaflet 1.9 pelo CDN. Nenhuma dependência nova.

**Storage**: PostgreSQL 16. Aeródromo passa a guardar a emenda e o tipo publicado. Modelo de avião guarda a frota e o estado do manual. O manual de cada modelo, fora o Cessna 140 da semente, nasce num arquivo JSON versionado em `servidor/manuais/` e é levado ao banco pelo comando de carga. O modelo ganha a massa do combustível por galão, tirada do manual, porque 4 dos 20 modelos queimam querosene de aviação. A rota do plano é uma lista ordenada de trechos.

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
| Número só do manual | Passa. O corte dos 20 modelos não autoriza número emprestado. | Passa. Cada número do arquivo cita documento e página. Arquivo incompleto não grava, e o modelo continua sem manual. Fator de unidade (lb, in, L, mph) é constante física, não número de avião. |
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
├── manuais.py              # valida os arquivos de manual e grava no banco
├── manuais/<modelo>.json   # um manual oficial por modelo do RAB
├── rota.py                 # escolha da rota e das escalas
├── calculo.py              # trecho, já existente, passa a ser chamado por perna
├── planos.py               # grava a rota no plano
└── pdf_plano.py            # imprime os trechos

alembic/versions/          # coluna da massa do combustível por galão
tests/test_manuais.py       # arquivo válido, arquivo incompleto, unidade convertida, experimental

templates/plano.html        # lista os trechos e desenha a linha já calculada
templates/plano_novo.html   # origem e destino no catálogo; não pede a escala
documentacao/piloto.md      # o que é escala, catálogo indisponível e modelo sem manual
```

**Structure Decision**: Continua o processo Flask do plano direto. Catálogo e rota entram em módulos novos. O navegador não ganha framework nem fórmula.

## Complexity Tracking

Nenhuma violação da constituição. A carga do ROTAER e do RAB usa o `requests` já justificado. Não entra biblioteca de grafo. O arquivo de manual é JSON lido pela biblioteca padrão do Python. As funções do comando de carga ficam pequenas, dentro do limite de complexidade de `tests/review/test_module_shape.py`.
