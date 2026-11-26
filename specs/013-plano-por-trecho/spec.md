# Feature Specification: Tela do plano organizada por trecho

**Feature Branch**: `013-plano-por-trecho`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User decision: alinhar a tela do plano calculado à experiência aprovada, com fichas por trecho, mapa restrito ao trecho ativo e METAR decodificado em português, mantendo o boletim original.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar cada trecho em sua própria ficha (Priority: P1)

Como piloto, quero alternar entre fichas identificadas pela origem e pelo destino de cada trecho, para consultar os dados do trecho ativo sem confundi-los com os demais.

**Why this priority**: A rota pode conter escalas; seus dados precisam ser apresentados na sequência e no contexto do trecho correto.

**Independent Test**: Abrir um plano de um e de vários trechos, alternar entre as fichas e confirmar o resumo fixo, os dados correspondentes a cada trecho e a seleção anunciada da ficha ativa.

**Acceptance Scenarios**:

1. **Given** um plano com um ou mais trechos, **When** o piloto abre o plano, **Then** vê o resumo do voo acima das fichas e uma ficha identificada para cada trecho.
2. **Given** um plano com vários trechos, **When** o piloto seleciona outra ficha, **Then** a ficha correspondente passa a ser a única ficha ativa e os dados exibidos pertencem àquele trecho.
3. **Given** a tela de um plano, **When** o piloto consulta os itens de checklist, **Then** a tela não oferece itens ou ações de marcar/desmarcar; o checklist sugerido continua disponível no PDF.
4. **Given** um plano com dados secundários ou sintéticos, **When** o piloto consulta qualquer ficha, **Then** os avisos de estimativa didática ou DEMO permanecem visíveis.

### User Story 2 - Consultar o mapa do trecho ativo (Priority: P1)

Como piloto, quero que o mapa da ficha mostre somente o trecho selecionado, com controles distintos para as bases e para o radar, para não confundir a rota inteira com a etapa atual.

**Why this priority**: Cada ficha deve permitir conferir visualmente sua própria perna sem ocultar o estado real das fontes de mapa.

**Independent Test**: Abrir uma rota com vários trechos, alternar fichas, bases e radar e verificar que somente o trecho ativo é desenhado e que indisponibilidades não são mascaradas.

**Acceptance Scenarios**:

1. **Given** um trecho ativo com coordenadas disponíveis, **When** o mapa é exibido, **Then** contém somente os pontos e a linha de origem e destino desse trecho.
2. **Given** uma rota com vários trechos, **When** o piloto troca de ficha, **Then** o mapa passa a mostrar somente o trecho da nova ficha e ajusta o enquadramento a esse trecho.
3. **Given** o mapa de ruas, carta visual oficial ou OpenAIP, **When** o piloto liga ou desliga o radar, **Then** apenas a sobreposição de radar muda; a base e a rota do trecho ativo permanecem.
4. **Given** a carta visual oficial indisponível ou sem validação dos requisitos de fonte e cobertura, **When** o piloto abre os controles do mapa, **Then** a carta aparece explicitamente como indisponível e não é substituída silenciosamente por ruas ou OpenAIP.
5. **Given** coordenadas, carta, OpenAIP ou radar indisponíveis, **When** o piloto consulta o trecho, **Then** a indisponibilidade é informada sem desenhar pontos ou camadas inventadas.

### User Story 3 - Ler a meteorologia do trecho (Priority: P1)

Como piloto, quero consultar os boletins da saída e da chegada do trecho ativo em blocos identificados, entender em português os dados METAR disponíveis e conferir o texto original.

**Why this priority**: A meteorologia deve ser legível sem perder a fonte primária ou atribuir ao boletim informações que ele não fornece.

**Independent Test**: Exibir METARs com dados estruturados disponíveis, boletins ausentes e grupos não decodificados; conferir campos e unidades traduzidos, texto original, fonte, horário e indisponibilidades.

**Acceptance Scenarios**:

1. **Given** um METAR disponível para a saída ou chegada, **When** o piloto consulta a ficha, **Then** vê identificação do aeródromo, campos que a fonte efetivamente fornece com rótulos em português, o METAR original, a fonte e o horário quando disponíveis.
2. **Given** um grupo METAR sem campo estruturado correspondente ou não suportado, **When** o boletim é apresentado, **Then** o texto original permanece íntegro e a interface não inventa uma interpretação.
3. **Given** METAR ou TAF ausente, **When** o piloto consulta a ficha, **Then** a ausência é informada para o aeródromo e tipo corretos, sem completar dados.
4. **Given** um TAF disponível, **When** o piloto consulta a ficha, **Then** o texto original é identificado como TAF e não é apresentado como previsão decodificada por esta feature.
5. **Given** mudança de ficha, **When** o piloto consulta os boletins, **Then** os blocos correspondem somente à saída e à chegada do trecho ativo.

### Edge Cases

- Um plano sem trechos não apresenta abas ou mapa de trecho e mantém visíveis seu estado e motivo.
- Um trecho sem coordenada de origem ou destino não desenha a rota inteira como substituto; o mapa do trecho informa indisponibilidade.
- A edição da WAC, georreferenciamento ou cobertura não passou pelos gates existentes: carta visual oficial permanece indisponível.
- OpenAIP não está autorizada, configurada ou acessível: a opção é marcada indisponível, sem substituir a carta.
- Radar sem URL ou limites geográficos válidos permanece desligado e indisponível.
- O METAR contém grupos desconhecidos, ausentes ou com valores nulos: somente dados retornados pela fonte são descritos; o original continua visível.
- A meteorologia não está disponível para um dos aeródromos: isso não oculta o boletim disponível para o outro.
- Em telas estreitas, as fichas podem ser percorridas horizontalmente e o conteúdo da ficha verticalmente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A tela MUST apresentar o resumo do voo acima de uma ficha por trecho, sem alterar os valores calculados no servidor.
- **FR-002**: Cada ficha MUST identificar sua origem e destino, indicar seu estado ativo de forma visual e acessível e apresentar somente os dados correspondentes àquele trecho.
- **FR-003**: A ordem de conteúdo de cada ficha MUST ser: grandezas do trecho, METAR da saída, METAR da chegada, mapa do trecho e sequência calculada.
- **FR-004**: A tela MUST NOT apresentar lista interativa de checklist; o checklist sugerido permanece disponível no PDF.
- **FR-005**: Avisos de segurança, estado inaceitável do plano, origem secundária ou perfil DEMO MUST permanecer visíveis e associados ao plano.
- **FR-006**: O mapa da ficha MUST desenhar somente os pontos e a linha do trecho ativo; MUST NOT exibir a rota completa ou dados de outro trecho como se fossem daquele trecho.
- **FR-007**: O mapa MUST oferecer controles visíveis e acessíveis para mapa de ruas, carta visual oficial, camada OpenAIP quando disponível e radar de chuva independente. Mapa de ruas é a base inicial e radar inicia desligado.
- **FR-008**: A carta MUST permanecer indisponível até que os gates existentes de edição vigente, georreferenciamento, cobertura, autorização e geração reproduzível sejam aprovados. Sua indisponibilidade MUST ser explícita e MUST NOT ser mascarada por outra camada.
- **FR-009**: OpenAIP MUST manter identificação não oficial, atribuição e disponibilidade conforme a especificação 010 e a constituição; MUST NOT ser apresentada como carta WAC.
- **FR-010**: Trocar ficha, base ou estado do radar MUST NOT recalcular nem modificar os pontos, dados ou aceitabilidade da rota recebida.
- **FR-011**: Para o trecho ativo, a interface MUST organizar METAR de saída e chegada em blocos próprios, exibir o texto original sem alteração e apresentar em português somente campos estruturados fornecidos pela fonte, com unidade, fonte e horário quando disponíveis.
- **FR-012**: Dados METAR não fornecidos ou não decodificados MUST ser indicados como indisponíveis ou não decodificados; a interface MUST NOT inferir, completar ou apresentar interpretação como dado oficial.
- **FR-013**: TAF MUST ser identificado separadamente e manter o texto original; esta feature MUST NOT decodificar TAF.
- **FR-014**: Falhas ou ausência de meteorologia, vento, carta, OpenAIP ou radar MUST permanecer explícitas, sem valores inventados ou substituição silenciosa.
- **FR-015**: Abas, controles de camada, radar e zoom MUST ser utilizáveis por teclado e toque, com foco visível, rótulos ligados e estados acessíveis.
- **FR-016**: Rótulos, explicações e avisos MUST permanecer em português; o mapa MUST preservar atribuições de suas fontes.
- **FR-017**: A interface MUST preservar o aviso de que o resultado é didático, não substitui manual, treinamento ou norma e não autoriza voo.
- **FR-018**: A feature MUST NOT alterar cálculo, persistência de rota, propriedade do plano ou conteúdo funcional do PDF, exceto manter o checklist sugerido nesse documento.
- **FR-019**: O sistema MUST obter e conservar a meteorologia de cada aeródromo distinto que aparece como saída ou chegada dos trechos; alternar fichas MUST NOT iniciar novas consultas externas.

### Key Entities *(include if feature involves data)*

- **Ficha do trecho**: Apresentação transitória de um trecho calculado, com origem, destino, grandezas, meteorologia, mapa e sequência.
- **Boletim meteorológico**: METAR ou TAF associado a um aeródromo, com texto original, campos estruturados, fonte, horário e estado de disponibilidade.
- **Camada do mapa**: Base de ruas, carta WAC oficial, OpenAIP suplementar ou radar, cada uma com disponibilidade e estado de seleção próprios.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os testes de tela, há uma ficha identificável por trecho; alternar fichas mostra somente os dados do trecho ativo e mantém o resumo acima delas.
- **SC-002**: Em todos os testes com mais de um trecho, o mapa desenha somente os dois pontos e a linha do trecho ativo; trocar de ficha atualiza o enquadramento sem alterar a rota calculada.
- **SC-003**: Em 100% dos testes, a WAC não validada, OpenAIP sem acesso, radar inválido ou meteorologia ausente aparece como indisponível, sem substituto ou valor inventado.
- **SC-004**: Em 100% dos METARs de teste, o original permanece íntegro; campos estruturados disponíveis são identificados em português com unidades e procedência, e dados ausentes ou não decodificados não recebem interpretação inventada.
- **SC-005**: Em 100% dos TAFs de teste, o conteúdo permanece original, claramente identificado e separado do METAR.
- **SC-006**: O checklist não é apresentado na tela do plano e continua disponível no PDF.
- **SC-007**: Em larguras de 390 px e 1440 px, abas, controles de mapa, radar e zoom são utilizáveis por teclado e toque, com estados acessíveis.

## Assumptions

- A experiência aprovada em `EXPERIENCE.md` é a referência de composição e ordem da ficha.
- O servidor continua responsável por cálculo, dados meteorológicos, autorização de camadas e preparação dos campos estruturados; o navegador apenas apresenta os dados recebidos e controla a visualização.
- A meteorologia de cada aeródromo da rota é consultada ao montar o plano e fica disponível à tela sem novas consultas quando o piloto alterna fichas.
- O METAR é decodificado somente a partir dos campos estruturados retornados pela fonte meteorológica existente. O boletim bruto permanece visível para conferência e nenhuma interpretação é feita de grupos sem suporte.
- O TAF permanece bruto nesta feature; sua decodificação está fora de escopo.
- A carta oficial continua sendo a WAC AISWEB/DECEA e permanece indisponível enquanto os gates da feature 009 não estiverem comprovados. OpenAIP segue a feature 010 e a constituição.
- A alteração se limita à tela do plano; o PDF e os cálculos permanecem inalterados.
