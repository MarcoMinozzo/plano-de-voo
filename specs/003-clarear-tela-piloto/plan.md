# Implementation Plan: Clarear a tela do piloto

**Branch**: `003-clarear-tela-piloto` | **Date**: 2026-11-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-clarear-tela-piloto/spec.md`

## Summary

A conta da rota não muda. A tela passa a devolver o que o piloto informou quando a conta recusa, a escolher aeródromo por texto, a pedir confirmação de hora só quando ela já passou, a dizer "aceitável para planejamento" ou "não aceitável", a omitir tabela vazia, a colocar o aviso do mapa de ruas junto do mapa, a abrir a alteração de um plano existente e a manter visível o item de checklist marcado.

A abordagem está em [research.md](./research.md). Não há dependência nova. O estado gravado do plano continua o de hoje; o rótulo em português é só o que a tela mostra.

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: As já nomeadas na constituição 2.2.0. Nenhuma dependência nova. Leaflet 1.9 continua pelo CDN, só para desenhar trechos já calculados.

**Storage**: PostgreSQL 16. Nenhum campo novo. O plano já guarda origem, destino, hora, aeronave, dados particulares, estado e itens de checklist.

**Testing**: pytest, com o cliente Flask e a base de teste já usada no plano direto. A lista nacional real não entra no teste.

**Target Platform**: O mesmo processo Flask local.

**Project Type**: Aplicação web de um processo. As páginas continuam servidas pelo servidor.

**Performance Goals**: A busca de aeródromo responde na interação de quem digita, sobre a emenda já carregada, sem baixar a lista nacional para o navegador.

**Constraints**: Sem fórmula de voo no JavaScript. A busca só pede correspondências ao servidor e mostra o retorno. Texto em português. O aviso educacional permanece. Chave de serviço continua fora do repositório. Uma recusa de formulário não substitui o plano já gravado.

**Scale/Scope**: Sete histórias de tela. O catálogo consultado é o da emenda vigente já especificado.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição 2.2.0. O nome do projeto é Plano de voo.

| Portão | Antes da pesquisa | Depois do desenho |
| --- | --- | --- |
| Spec antes do código | Passa. Este plano não altera o servidor. | Passa. Artefatos em `specs/003-clarear-tela-piloto/`. |
| Cálculo no servidor | Passa. A rota não muda. | Passa. O JavaScript da busca não calcula voo. |
| Unidade, fonte e falha visível | Passa. "Indisponível" continua sendo a falta de fonte. | Passa. A tabela de grandezas só aparece com unidade e fonte. |
| Aviso educacional | Passa. | Passa. Tela e PDF mantêm o aviso. |
| Plano só do piloto da sessão | Passa. A alteração reusa a sessão. | Passa. Plano de outro piloto continua recusado. |
| Nenhuma dependência nova | Passa. | Passa. |

## Project Structure

### Documentation (this feature)

```text
specs/003-clarear-tela-piloto/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tela-piloto.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py
templates/
├── base.html
├── painel.html
├── plano_novo.html
└── plano.html
servidor/planos.py
tests/test_tela_piloto.py
```

**Structure Decision**: A aplicação continua um processo Flask. A tela muda em `templates/` e nas rotas de `app.py`. A conta em `servidor/rota.py` e `servidor/calculo.py` não muda. O rótulo de planejamento é função de apresentação, não coluna nova.

## Complexity Tracking

Nenhuma violação da constituição. Esta seção não se aplica.
