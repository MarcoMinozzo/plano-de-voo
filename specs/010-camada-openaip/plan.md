# Implementation Plan: Camada aeronáutica OpenAIP

**Branch**: `010-camada-openaip` | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/010-camada-openaip/spec.md`

## Summary

Adicionar OpenAIP como uma opção de mapa selecionável no Leaflet, sem
apresentá-la como WAC oficial. Usar os tiles PNG TMS combinados do provedor
como base própria; ruas continuam sendo a base inicial e o radar segue como
overlay independente. Requisitar os tiles pelo servidor, com chave apenas no
ambiente e validação de que o plano pertence ao piloto autenticado. Não alterar
o cálculo, a rota, o banco ou a disponibilidade da carta WAC AISWEB.

## Technical Context

**Language/Version**: Python 3.10+; Jinja, HTML, CSS e JavaScript existentes.

**Primary Dependencies**: Flask 3.0, requests 2.31 e Leaflet 1.9 via CDN.
Todas já existem; nenhuma dependência nova.

**Storage**: PostgreSQL existente. Não persistir tiles nem adicionar migração.

**Testing**: pytest. Testes focados em `tests/test_openaip.py` e
`tests/test_tela_piloto.py`, com serviço remoto simulado.

**Target Platform**: Aplicação Flask em navegadores móveis e desktop.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Não requisitar OpenAIP até seleção explícita. Cada
requisição externa tem timeout finito; falhas e limites do provedor não podem
bloquear a abertura do plano nem gerar repetição automática ilimitada.

**Constraints**: A chave OpenAIP fica no servidor, fora do repositório e da
página. A licença CC BY-NC 4.0, o uso não comercial e a atribuição do provedor
devem ser respeitados. O PNG OpenAIP é um mapa combinado, não uma carta WAC;
ruas, OpenAIP e a carta AISWEB não podem ser confundidas. Só buscar tiles do
host fixo do provedor e aceitar coordenadas limitadas. Restringir cada tile ao
piloto dono do plano. Não calcular rota no navegador nem substituir
silenciosamente AISWEB. Sem nova dependência, armazenamento ou cache local.

**Scale/Scope**: Uma camada base opcional por mapa aberto. Nenhuma alteração
persistente por plano.

## Constitution Check

| Princípio | Estado | Evidência / salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são preparados antes do runtime. |
| II. Limite educacional | PASS | Identificação não oficial e aviso de que a camada não valida ou autoriza voo. |
| III. Cálculo no servidor | PASS | OpenAIP é somente apresentação cartográfica; rota e cálculo permanecem no servidor. |
| IV. Unidades, fonte e indisponibilidade | PASS | Atribuição OpenAIP visível; indisponibilidade explícita; sem fallback enganoso. |
| V. Pilha pequena e banco relacional | PASS | Reutilizar Flask, requests e Leaflet; sem dependência, tabela ou persistência nova. |
| Segurança e acesso por piloto | PASS | Endpoint exige sessão e verifica a propriedade do plano antes de buscar tile. |

Nenhuma violação constitucional identificada.

## Project Structure

### Documentation (this feature)

```text
specs/010-camada-openaip/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tiles-openaip.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py                       # rota autenticada de proxy para tiles
servidor/
└── openaip.py               # validação e busca no host fixo OpenAIP
templates/
└── plano.html               # seletor de ruas/OpenAIP e eventos de falha
.env.example                 # declaração da variável sem valor secreto
documentacao/
└── operacao.md              # configuração, atribuição e disponibilidade
tests/
├── test_openaip.py          # proxy, falhas e acesso ao plano
└── test_tela_piloto.py      # seletor, radar e rota preservada
```

**Structure Decision**: Flask/Jinja existente. A API de tiles será acessada
por um proxy autenticado do próprio servidor para que a chave não chegue ao
navegador. O mapa OpenAIP será uma base selecionável, não uma sobreposição
transparente sobre ruas. O radar continua usando a camada independente já
existente.

## Phase 0: Outline & Research

- [research.md](./research.md) registra o contrato oficial de tiles, a licença,
  a atribuição, o acesso por chave e as decisões de disponibilidade.
- O serviço PNG usa o layer combinado `openaip`, coordenadas TMS e zoom mínimo
  2; Leaflet deve usar a opção TMS apropriada.
- O provedor recomenda cache para reduzir requisições. Este plano não adiciona
  cache persistente; respostas devem respeitar somente as diretivas de cache
  que o provedor enviar. Limites ou erros deixam a camada indisponível.
- Nenhum ponto técnico permanece sem esclarecimento para iniciar o design.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) descreve estado de disponibilidade e tiles
  sem entidade persistente.
- [contracts/tiles-openaip.md](./contracts/tiles-openaip.md) define o endpoint
  autenticado, a validação de propriedade, o formato de resposta e as falhas.
- [quickstart.md](./quickstart.md) define configuração local, testes simulados
  e verificação manual da camada e da atribuição.
- Reavaliação da constituição: PASS. A carta oficial AISWEB permanece separada;
  OpenAIP não afeta cálculo, não é fallback da carta e exige licença,
  atribuição e segredo fora do repositório.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
