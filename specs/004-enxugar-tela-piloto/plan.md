# Implementation Plan: Enxugar a tela do piloto

**Branch**: `004-enxugar-tela-piloto` | **Date**: 2026-11-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-enxugar-tela-piloto/spec.md`

## Summary

A conta da rota, da reserva, do vento e do pôr do sol não muda. O formulário passa a pedir só tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem. O peso das pessoas inclui o piloto e é o total informado. O combustível da carga é o de planejamento já gravado no manual, não um valor digitado.

A abordagem está em [research.md](./research.md). Não há dependência nova.

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: As já nomeadas na constituição 2.2.0. Nenhuma dependência nova. Leaflet 1.9 continua pelo CDN, só quando a rota tem ao menos dois pontos.

**Storage**: PostgreSQL 16. Nenhum campo novo.

**Testing**: pytest, com o cliente Flask e a base de teste já usada. A lista nacional real não entra no teste.

**Target Platform**: O mesmo processo Flask local.

**Project Type**: Aplicação web de um processo. As páginas continuam servidas pelo servidor.

**Performance Goals**: A página do plano novo cabe na primeira leitura: caixas de uma linha, dois grupos e o botão de calcular sem o texto longo aberto.

**Constraints**: Sem fórmula de voo no JavaScript. O filtro, quando a lista passa de doze, só esconde opções já renderizadas. O texto casa com parte do código ou do nome mostrado, sem maiúsculas nem acentos, e não usa a cidade. Texto em português. Unidade e fonte continuam nomeadas. O combustível de planejamento continua o valor gravado na aeronave; a tela não o copia para uma constante. Esta feature não carrega o ROTAER nem o RAB e não inventa aeródromo ou modelo. O PDF continua com unidade e fonte em cada grandeza e com o texto do piloto. Chave de serviço continua fora do repositório.

**Scale/Scope**: Três histórias de tela. Formulário, plano calculado e checklist. Entrada, cadastro e painel só herdam o visual.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição 2.2.0. O nome do projeto é Plano de voo.

| Portão | Antes da pesquisa | Depois do desenho |
| --- | --- | --- |
| Spec antes do código | Passa. Este plano não altera o servidor. | Passa. Artefatos em `specs/004-enxugar-tela-piloto/`. |
| Cálculo no servidor | Passa. A rota não muda. A carga soma os pesos informados e o combustível do manual no servidor. | Passa. O JavaScript não calcula voo nem combustível. |
| Unidade, fonte e falha visível | Passa. A fonte gravada continua na tela, uma vez por grandeza. | Passa. Célula diferente repete unidade e fonte. O PDF não muda. |
| Aviso educacional | Passa. A frase de que não autoriza o voo fica visível. | Passa. O texto completo fica na tela do plano, fechado, e no PDF. |
| Plano só do piloto da sessão | Passa. Nenhuma rota nova. | Passa. |
| Nenhuma dependência nova | Passa. | Passa. Estilo e filtro no HTML já servido. O filtro não grava cidade nem aeródromo. |

## Project Structure

### Documentation (this feature)

```text
specs/004-enxugar-tela-piloto/
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
├── plano_novo.html
├── plano.html
├── painel.html
servidor/calculo.py
servidor/planos.py
documentacao/piloto.md
tests/test_tela_piloto.py
tests/test_calculo.py
tests/conftest.py
```

**Structure Decision**: A aplicação continua um processo Flask. A tela muda em `templates/plano_novo.html`. A carga muda em `servidor/calculo.py` e a leitura dos dados deste voo em `servidor/planos.py`. `servidor/rota.py` e `servidor/pdf_plano.py` não mudam.

## Complexity Tracking

Nenhuma violação da constituição. Esta seção não se aplica.
