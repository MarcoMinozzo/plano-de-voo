# Feature Specification: Mapa interativo com carta e radar

**Feature Branch**: `main` (nenhuma branch de feature criada)

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "Reveja como estão sendo apresentados mapa, carta e informação meteorológica e de radar de chuvas; permita escolher entre mapa de ruas e carta aérea e sobrepor ou não radar."

## Clarifications

### Session 2026-11-25

- Q: Qual caminho devo registrar para disponibilizar a carta visual no mapa? → A: Avaliar a carta WAC GeoPDF oficial do AISWEB como camada local georreferenciada, sem implementação até validar arquivo vigente, cobertura da rota, autorização de uso e ambiente de geração compatível.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escolher camadas do mapa (Priority: P1)

Como piloto, quero escolher entre mapa de ruas e carta visual e controlar o radar separadamente, para consultar a rota com as camadas que preciso.

**Why this priority**: A alternância explícita de bases e o controle de radar são o principal pedido de interação no mapa.

**Independent Test**: Com rota e camadas disponíveis, alternar entre as duas bases, ligar e desligar o radar em cada uma e confirmar que a rota permanece visível.

**Acceptance Scenarios**:

1. **Given** uma rota e as duas bases disponíveis, **When** o piloto seleciona uma base, **Then** ela passa a ser exibida e a rota permanece visível.
2. **Given** qualquer base disponível, **When** o piloto liga ou desliga o radar, **Then** somente a sobreposição muda e a base selecionada permanece.
3. **Given** carta ou radar indisponível, **When** o piloto abre ou controla o mapa, **Then** a indisponibilidade é indicada sem substituição silenciosa ou camada enganosa.

---

### User Story 2 - Consultar meteorologia (Priority: P2)

Como piloto, quero consultar METAR e TAF em blocos técnicos organizados por aeródromo, para localizar rapidamente os dados relevantes sem textos redundantes.

**Why this priority**: A apresentação deve ser mais clara, mantendo a informação original e sua procedência.

**Independent Test**: Abrir um plano com boletins disponíveis e ausentes; confirmar agrupamento, rótulos, fonte e horário quando fornecidos, além da indicação explícita de campos indisponíveis.

**Acceptance Scenarios**:

1. **Given** METAR ou TAF disponível, **When** o piloto consulta a ficha, **Then** o boletim aparece identificado por aeródromo e tipo, com campos, texto original, fonte e horário fornecidos.
2. **Given** boletim ou campo ausente, **When** o piloto consulta a ficha, **Then** a ausência é indicada sem inferir valores ou completar o boletim.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST oferecer controles visíveis no topo do mapa para escolher entre mapa de ruas e carta visual, com somente uma base ativa por vez.
- **FR-002**: O mapa de ruas MUST ser a base inicial.
- **FR-003**: O sistema MUST iniciar com o radar desligado e permitir ligá-lo ou desligá-lo independentemente da base selecionada.
- **FR-004**: A rota MUST permanecer visível ao trocar a base ou o estado do radar; a interface MUST NOT recalcular nem alterar os dados de rota recebidos.
- **FR-005**: O sistema MUST indicar quando a carta visual ou o radar não estiverem disponíveis; MUST NOT apresentar ruas como carta nem desenhar radar sem dados geográficos válidos.
- **FR-006**: O sistema MUST organizar METAR/TAF por aeródromo e tipo, mantendo identificáveis o texto original e os campos retornados.
- **FR-007**: O sistema MUST exibir fonte e horário quando fornecidos e indicar dados ausentes sem inferir ou interpretar valores.
- **FR-008**: Os controles e o zoom MUST ser utilizáveis por toque e teclado em telas móveis e desktop.
- **FR-009**: Os rótulos e mensagens MUST permanecer em português.
- **FR-010**: A ficha MUST preservar o aviso existente de que meteorologia apresentada não substitui avaliação operacional nem autoriza voo.
- **FR-011**: A carta MUST ser considerada disponível no mapa somente quando a edição oficial WAC selecionada para a rota tiver georreferenciamento válido e cobrir todos os pontos da rota; caso contrário, a interface MUST indicar indisponibilidade sem exibir uma carta desalinhada.

### Key Entities *(include if feature involves data)*

- **Base cartográfica**: Mapa de ruas ou carta visual, com estado disponível/indisponível e seleção ativa.
- **Sobreposição de radar**: Imagem de precipitação e cobertura geográfica, independente da base cartográfica.
- **Rota do plano**: Pontos e trechos calculados fora da interface, desenhados sem alteração.
- **Boletim meteorológico**: METAR ou TAF associado a aeródromo, com texto, campos, fonte, horário e estado de disponibilidade.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos cenários testados com bases disponíveis, o piloto consegue alternar entre ruas e carta sem perder a rota.
- **SC-002**: Em 100% dos cenários testados, o radar inicia desligado; quando disponível, pode ser ligado e removido sem trocar a base selecionada.
- **SC-003**: Em todos os cenários testados de carta, radar ou boletim indisponíveis, a ficha informa a ausência e não apresenta substituto ou valor inventado.
- **SC-004**: Em telas de 390 px e 1440 px, os controles do mapa e o zoom permanecem utilizáveis por toque e teclado.
- **SC-005**: Em 100% dos boletins testados, aeródromo e tipo são identificáveis e fonte/horário aparecem quando fornecidos.
- **SC-006**: Em 100% dos cenários testados, a carta atual cobre os pontos da rota ou aparece explicitamente como indisponível; nenhuma carta sem georreferenciamento validado é exibida no mapa.

## Assumptions

- O mapa de ruas permanece selecionado inicialmente, conforme o comportamento atual e as referências de UX do projeto.
- O radar inicia desligado; o piloto o ativa explicitamente quando desejar a sobreposição.
- A fonte oficial da carta permanece AISWEB/DECEA. O caminho selecionado para avaliação é usar a WAC GeoPDF local georreferenciada, sujeita à validação do arquivo atual, cobertura da rota, autorização de uso e ambiente de geração.
- Até todas essas condições serem atendidas, a carta do mapa permanece indisponível; a aplicação não troca silenciosamente para WMS nem apresenta um PDF sem georreferenciamento como camada cartográfica.
- Se a carta oficial ou o radar não puderem ser georreferenciados ou carregados, a ficha informa indisponibilidade; não há fallback que represente uma camada como outra.
- Os dados meteorológicos continuam sendo fornecidos pelas fontes existentes; esta feature reorganiza sua apresentação, sem produzir avaliação meteorológica operacional.
