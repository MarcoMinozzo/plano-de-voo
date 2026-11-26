# Feature Specification: Camada aeronáutica OpenAIP

**Feature Branch**: `010-camada-openaip`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User decision: permitir OpenAIP como camada aeronáutica suplementar e não oficial no mapa.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar dados aeronáuticos comunitários (Priority: P1)

Como piloto, quero selecionar uma camada de dados aeronáuticos OpenAIP
separada do mapa de ruas e da carta WAC, para consultar informações
aeronáuticas adicionais sem confundi-las com uma carta oficial.

**Why this priority**: É a fonte alternativa disponível para visualizar dados
aeronáuticos enquanto a carta WAC oficial não pode ser servida como camada.

**Independent Test**: Abrir um plano com rota, selecionar OpenAIP quando
disponível e confirmar o rótulo, a atribuição, a rota preservada e a distinção
em relação à carta WAC.

**Acceptance Scenarios**:

1. **Given** um plano e a camada OpenAIP disponível, **When** o piloto a
   seleciona, **Then** os dados aeronáuticos aparecem como uma opção distinta
   de mapa, identificada como OpenAIP comunitária e não oficial.
2. **Given** OpenAIP selecionada e radar desligado, **When** o piloto liga ou
   desliga o radar, **Then** somente o radar muda e a camada OpenAIP permanece
   selecionada.
3. **Given** OpenAIP indisponível, **When** o piloto abre ou seleciona a
   camada, **Then** recebe uma indicação explícita e as demais opções de mapa
   não são trocadas silenciosamente.
4. **Given** uma rota visível, **When** o piloto troca a opção de mapa ou o
   radar, **Then** os pontos, trechos e zoom da rota permanecem inalterados.

### Edge Cases

- A autorização de acesso não está configurada, expirou ou foi recusada.
- O serviço não entrega dados para a região ou nível de zoom solicitado.
- O mapa está em zoom inferior ao aceito pela camada OpenAIP.
- A atribuição exigida não pode ser exibida junto da camada.
- Os termos ou a licença deixam de permitir o uso não comercial previsto.
- Uma falha da camada ocorre enquanto o mapa de ruas ou a carta WAC está ativa.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O piloto MUST poder selecionar OpenAIP como uma opção
  aeronáutica suplementar, distinta do mapa de ruas e da carta WAC oficial.
- **FR-002**: A opção MUST ser identificada visivelmente como “OpenAIP — dados
  aeronáuticos comunitários; não é carta WAC nem fonte oficial” e MUST NOT ser
  apresentada como substituta da carta oficial ou como garantia de navegação.
- **FR-003**: A atribuição exigida pelo provedor MUST permanecer visível
  enquanto a camada estiver sendo exibida.
- **FR-004**: A camada MUST ficar indisponível se o acesso válido, a atribuição
  ou a permissão de uso não puderem ser confirmados, incluindo a condição de
  uso não comercial da licença CC BY-NC 4.0. A interface MUST explicar a
  indisponibilidade sem expor credenciais.
- **FR-005**: OpenAIP MUST ser ativada somente por escolha explícita do piloto;
  o mapa de ruas continua sendo a opção inicial.
- **FR-006**: OpenAIP e o radar MUST ser controles independentes. Ligar ou
  desligar o radar MUST NOT trocar a opção de mapa selecionada.
- **FR-007**: Trocar a opção de mapa ou o radar MUST NOT alterar os pontos,
  trechos, zoom ou cálculos da rota recebida pelo mapa.
- **FR-008**: Falha ou indisponibilidade de OpenAIP MUST NOT causar substituição
  silenciosa por ruas, WAC ou outra fonte, nem ocultar o estado da carta AISWEB.
- **FR-009**: Os controles, avisos e atribuições apresentados ao piloto MUST
  permanecer em português, exceto nomes próprios e termos oficiais de licença.
- **FR-010**: Os dados OpenAIP MUST NOT ser usados como entrada ou validação do
  cálculo de rota, combustível ou aceitabilidade do plano.

### Key Entities

- **Opção de mapa**: ruas, carta WAC oficial ou dados aeronáuticos OpenAIP,
  com estado de disponibilidade e seleção explícita.
- **Atribuição da fonte**: identificação visível do provedor associada à
  camada OpenAIP.
- **Sobreposição de radar**: estado ligado/desligado independente da opção de
  mapa.
- **Rota do plano**: pontos e trechos calculados fora do mapa e preservados ao
  alternar camadas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os testes com OpenAIP disponível, o piloto consegue
  selecioná-la e distinguir sua identificação da carta WAC oficial.
- **SC-002**: Em 100% dos testes, a atribuição exigida aparece enquanto a
  camada OpenAIP está ativa.
- **SC-003**: Em 100% dos testes com falta de autorização, indisponibilidade
  regional ou falha de serviço, o piloto recebe aviso explícito sem troca
  silenciosa de fonte.
- **SC-004**: Em 100% dos testes, trocar a opção de mapa ou o radar preserva a
  rota e não altera qualquer resultado do cálculo.

## Assumptions

- O mapa de ruas permanece selecionado inicialmente, conforme o comportamento
  definido para o mapa existente.
- OpenAIP é uma opção aeronáutica comunitária suplementar, não uma WAC nem uma
  fonte oficial, e não substitui a carta AISWEB.
- A organização fornecerá e manterá a autorização de acesso necessária fora
  do repositório; nenhum segredo será solicitado ou gravado nesta especificação.
- A licença CC BY-NC 4.0 só será usada enquanto o uso do produto e a forma de
  exibição forem compatíveis com seus termos e com a exigência não comercial.
- A rota, o radar e a carta AISWEB mantêm seus estados independentes da camada
  OpenAIP.
