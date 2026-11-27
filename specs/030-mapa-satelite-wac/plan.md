# Implementation Plan: Mapa quadrado com satélite REDEMET e WAC visível

**Branch**: `main` | **Date**: 2026-11-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/030-mapa-satelite-wac/spec.md`

## Summary

Manter o mapa de ruas como base, adicionar uma sobreposição REDEMET consultada somente quando ativada, manter a opção WAC visível inclusive indisponível e ajustar a proporção do mapa em desktop. A rota e os dados persistidos não mudam. WAC continua como documento AISWEB; nenhum tile ou raster é criado nesta mudança.

## Technical Context

**Language/Version**: Python 3.10+; JavaScript, Jinja e CSS existentes.

**Primary Dependencies**: Flask, requests e Leaflet 1.9 já presentes. Nenhuma dependência nova.

**Storage**: PostgreSQL existente; não alterar modelo nem persistir o estado das camadas.

**Testing**: pytest focado em `tests/test_tempo.py` e `tests/test_tela_piloto.py`; build CSS existente.

**Target Platform**: Aplicação web Flask em navegadores móveis e desktop.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Não consultar a REDEMET ao abrir o plano; consultar somente após ativação do controle.

**Constraints**: Chave REDEMET só no servidor; endpoint do plano exige autenticação e propriedade. Validar URL HTTPS, host REDEMET esperado, data e limites geográficos. Manter a rota acima das imagens; estados indisponíveis explícitos. Não apresentar PDF ou mapa de ruas como WAC.

**Scale/Scope**: Um frame de satélite por ativação, um mapa por ficha ativa; sem alteração de cálculo, banco ou outras camadas.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são concluídos antes de editar servidor, template ou CSS. |
| II. Limite educacional | PASS | Preservar o aviso existente; camada visual não é apresentada como orientação operacional. |
| III. Cálculo no servidor | PASS | A interface só apresenta imagens e controla camadas; a rota permanece intacta. |
| IV. Fonte e indisponibilidade | PASS | Mostrar REDEMET e horário; não desenhar imagem sem metadados e limites válidos. |
| V. Pilha pequena e banco relacional | PASS | Reutilizar requests/Flask/Leaflet e chave existente; sem dependência, migração ou persistência nova. |
| Isolamento por piloto | PASS | Endpoint da camada usa a verificação de propriedade existente. |
| Carta AISWEB | PASS | A opção informa indisponibilidade; não produzir tiles WAC sem os gates da feature 009. |

Nenhuma violação constitucional identificada.

## Project Structure

```text
app.py
servidor/tempo.py
templates/plano.html
static/css/input.css
static/css/tailwind.css
tests/test_tempo.py
tests/test_tela_piloto.py
documentacao/piloto.md
specs/030-mapa-satelite-wac/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/camadas-satelite.md
├── quickstart.md
└── tasks.md
```

**Structure Decision**: Reutilizar o monólito Flask, o resolvedor de radar em `servidor/tempo.py`, a rota autenticada de camada em `app.py` e o widget Leaflet em `templates/plano.html`. O CSS de origem é `static/css/input.css`; regenerar `tailwind.css` pelo script existente.

## Phase 0: Outline & Research

- Evidências e decisões estão em [research.md](./research.md).
- Usar o endpoint oficial REDEMET do produto `realcada`; tomar horário e limites do retorno, sem valores geográficos fixos.
- Selecionar o frame mais recente com URL, hora e limites válidos. Restringir a URL de imagem ao host oficial observado; se a fonte mudar ou os metadados forem inválidos, deixar a camada indisponível.
- O endpoint da aplicação só chama a fonte após ação explícita e depois de verificar a sessão e a propriedade do plano.
- Não há clarificações pendentes nem escolhas de dependência.

## Phase 1: Design & Contracts

- O estado da imagem é efêmero e não altera o plano; detalhes em [data-model.md](./data-model.md).
- Contrato autenticado da camada e estados de resposta em [contracts/camadas-satelite.md](./contracts/camadas-satelite.md).
- Passos de teste e validação visual em [quickstart.md](./quickstart.md).
- WAC mantém o diálogo atual para documentos AISWEB válidos; estado sem documentos fica visível e desabilitado. Nenhum endpoint ou processamento de tiles WAC é criado.
- Revalidar a constituição: nenhum cálculo no navegador, segredo exposto, fallback enganoso, dado inventado, migração ou dependência nova.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
