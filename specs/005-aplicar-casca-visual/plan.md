# Implementation Plan: Aplicar a casca visual

**Branch**: `005-aplicar-casca-visual` | **Date**: 2026-11-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-aplicar-casca-visual/spec.md`

## Summary

Todas as telas passam a usar a planta da pista e o emblema. A entrada, o cadastro e o plano novo ficam num card de vidro. O envio esconde o card e mostra "Em processamento" até a resposta. O plano calculado ganha um resumo acima dos trechos. O menu autenticado oferece Novo voo, Voos planejados, Imprimir voo e Sair.

A abordagem está em [research.md](./research.md). Não há dependência nova. A conta, a ficha, o METAR, a carta, o radar e o checklist permanecem os de `specs/004-enxugar-tela-piloto/spec.md`.

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: As já nomeadas na constituição 2.2.0. Nenhuma dependência nova. O estilo continua no HTML servido. Leaflet 1.9 continua pelo CDN, só quando a rota tem ao menos dois pontos.

**Storage**: PostgreSQL 16. Nenhum campo novo. A planta e o emblema são arquivos em `static/casca/`.

**Testing**: pytest, com o cliente Flask e a base de teste já usada.

**Target Platform**: O mesmo processo Flask local, no navegador, inclusive em largura abaixo de 720 px.

**Project Type**: Aplicação web de um processo. As páginas continuam servidas pelo servidor.

**Performance Goals**: A troca de casca não acrescenta pedido de rede além das imagens da planta e do emblema. A ampulheta aparece no próprio envio, sem uma rota de espera.

**Constraints**: Sem fórmula de voo no JavaScript. O script da página só esconde o card, mostra a ampulheta e segura o menu até a resposta. Texto em português. Unidade, fonte e indisponível continuam como na 004. Sair continua encerrando a sessão. Chave de serviço continua fora do repositório. Sem biblioteca visual nova e sem arquivo de fonte novo.

**Scale/Scope**: Quatro histórias. Casca comum, card de entrada e de plano novo, espera do cálculo, resumo e menu. O miolo da ficha não é reescrito aqui.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição 2.2.0. O nome do projeto é Plano de voo.

| Portão | Antes da pesquisa | Depois do desenho |
| --- | --- | --- |
| Spec antes do código | Passa. Este plano não altera o servidor. | Passa. Artefatos em `specs/005-aplicar-casca-visual/`. |
| Cálculo no servidor | Passa. A conta não muda. | Passa. O script do envio não calcula voo, tempo, carta nem PDF. |
| Unidade, fonte e falha visível | Passa. A casca não preenche dado ausente. | Passa. O contrato deixa o miolo da ficha na 004. |
| Aviso educacional | Passa. A frase de que não autoriza o voo fica visível. | Passa. O card do plano novo a mostra sem um clique. |
| Plano só do piloto da sessão | Passa. Nenhuma lista nova. | Passa. Voos planejados continua sendo o painel da sessão. |
| Nenhuma dependência nova | Passa. | Passa. Duas imagens em `static/casca/` e o estilo em `templates/base.html`. |
| Senha e sessão | Passa. Oito caracteres, a frase única de recusa e o sair permanecem. | Passa. Sair continua um envio, não um link de leitura. |

## Project Structure

### Documentation (this feature)

```text
specs/005-aplicar-casca-visual/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── casca-visual.md
└── tasks.md
```

### Source Code (repository root)

```text
templates/
├── base.html
├── entrar.html
├── cadastro.html
├── plano_novo.html
├── plano.html
├── painel.html
static/casca/
├── blueprint-airport-runway.jpg
├── emblema-plano-de-voo.png
tests/test_casca_visual.py
```

**Structure Decision**: A aplicação continua um processo Flask. A casca mora em `templates/base.html` e nos templates que já existem. As imagens ficam em `static/casca/`. `servidor/`, `app.py` e o PDF não mudam de regra. O teste novo confere o contrato em `contracts/casca-visual.md`.

## Complexity Tracking

Nenhuma violação da constituição. Esta seção não se aplica.
