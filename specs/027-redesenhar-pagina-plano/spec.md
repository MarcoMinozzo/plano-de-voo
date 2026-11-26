# Feature Specification: Redesenho da página do plano

**Feature Branch**: `027-redesenhar-pagina-plano`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Redesenhar a página do plano de voo para melhorar o layout e o mapa, destacar alertas, mostrar nomes e contatos dos aeródromos e remover mensagens e blocos desnecessários."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entender a rota e os dados do plano (Priority: P1)

Como piloto, quero ver a rota completa, os dados dos aeródromos e os alertas em uma página organizada, para localizar rapidamente as informações relevantes.

**Why this priority**: A rota e seus limites são o conteúdo central do plano.

**Independent Test**: Abrir um plano de teste com escalas, alertas e dados de aeródromos disponíveis ou ausentes; conferir o resumo, as fichas e os avisos.

**Acceptance Scenarios**:

1. **Given** um plano com escalas, **When** o piloto abre a página, **Then** o primeiro card mostra a sequência completa de origem a destino.
2. **Given** qualquer trecho, **When** o piloto consulta sua ficha, **Then** origem e destino aparecem com nome oficial completo; ICAO permanece nos títulos e nas abas.
3. **Given** origem ou destino com dados publicados no ROTAER, **When** o piloto consulta o card da rota, **Then** são apresentados nome, ICAO, tipo, coordenadas, elevação, edição/data e contatos publicados.
4. **Given** contato não publicado, **When** o card do aeródromo é exibido, **Then** o contato aparece como indisponível, sem valor inventado.
5. **Given** alerta de excesso de peso ou outro limite excedido, **When** o plano é exibido, **Then** o alerta aparece em vermelho e continua identificável por texto.

### User Story 2 - Consultar o mapa sem perder a rota (Priority: P1)

Como piloto, quero controles claros para mapa de ruas e radar, para consultar as camadas sem confundi-las com uma carta oficial.

**Why this priority**: A apresentação atual mistura estados de camadas e a cobertura RainViewer reduz a legibilidade do mapa.

**Independent Test**: Alternar mapa de ruas e os radares em um plano de teste, incluindo estados disponíveis e indisponíveis, e verificar a rota e a legibilidade da base.

**Acceptance Scenarios**:

1. **Given** o mapa do trecho, **When** o piloto o abre, **Then** os controles aparecem dentro do mapa e no topo, com mapa de ruas ativo inicialmente.
2. **Given** a chave Google Maps não configurada, **When** os controles aparecem, **Then** Google Maps é mostrado desativado e não substitui o mapa de ruas.
3. **Given** radar oficial ou suplementar ativo, **When** o piloto altera uma camada, **Then** a base e a rota permanecem visíveis e cada radar continua identificado pela própria fonte.
4. **Given** RainViewer ativo, **When** o mapa é exibido, **Then** a camada de cobertura não obscurece o mapa e permanecem visíveis crédito, horário e aviso conciso de cobertura.
5. **Given** carta WAC indisponível ou camada não configurada, **When** o piloto consulta o mapa, **Then** o estado é informado de forma concisa e nenhuma fonte é apresentada como substituta.

### Edge Cases

- Em telas estreitas, campos e controles permanecem utilizáveis sem rolagem horizontal.
- Se nome, coordenada, elevação ou contato não existir na publicação oficial, o dado ausente é indicado sem estimativa.
- Se imagem, tile ou limites geográficos do radar forem inválidos, a camada é removida e a indisponibilidade é informada.
- Se houver dados de rota incompletos, os dados ausentes não são inferidos e o restante da página continua legível.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A página MUST agrupar o resumo, as fichas e os demais cards em um card principal; em telas largas, sua largura MUST ser aproximadamente 80% da viewport e, em telas estreitas, MUST adaptar-se à largura útil.
- **FR-002**: O primeiro card MUST apresentar a rota completa de origem a destino, incluindo as escalas, em ordem.
- **FR-003**: Cada ficha MUST exibir os nomes oficiais completos de origem e destino; os códigos ICAO MUST permanecer nos títulos e abas.
- **FR-004**: A página MUST exibir para origem e destino os campos oficiais disponíveis: nome, ICAO, tipo, coordenadas, elevação, edição/data ROTAER e contato AISWEB/ROTAER publicado. Dados ausentes MUST ser identificados como indisponíveis, sem estimativa.
- **FR-005**: Alertas de excesso de peso e outros limites excedidos MUST ser destacados em vermelho e por texto, sem alterar a mensagem ou o cálculo recebido.
- **FR-006**: Controles para mapa de ruas, Google Maps e radar MUST aparecer dentro do mapa, no topo, e ser utilizáveis por toque e teclado. Mapa de ruas MUST iniciar ativo. Google Maps MUST permanecer desativado até haver chave configurada localmente.
- **FR-007**: REDEMET MUST permanecer como radar oficial, independente da base e do RainViewer. RainViewer MUST permanecer suplementar e não oficial, com crédito vinculado, horário da fonte e aviso conciso sobre cobertura quando ativo.
- **FR-008**: A exibição de radar MUST preservar a geometria da rota e manter a base cartográfica legível; limites geográficos inválidos ou falhas de imagem/tile MUST resultar em camada indisponível, sem fallback silencioso.
- **FR-009**: Enquanto a WAC não passar pelos critérios de validação, a página MUST identificá-la como indisponível de forma concisa. OpenAIP não configurado MUST NOT gerar um bloco de aviso nem aparecer como uma camada disponível.
- **FR-010**: O estado desligado do radar MUST ser comunicado pelo controle, sem mensagem redundante de “radar desativado”.
- **FR-011**: A página MUST remover “Como ler este plano” e o link de PDF do rodapé, mantendo a ação de impressão no topo e o aviso geral didático e de não autorização de voo.
- **FR-012**: A reformulação MUST NOT alterar cálculos, dados persistidos da rota, acesso por piloto ou conteúdo do PDF.
- **FR-013**: Textos, unidades, fontes e estados MUST permanecer em português e não depender apenas de cor.

### Key Entities

- **Aeródromo**: publicação oficial com identificador, nome, tipo, posição, elevação, edição/data e contatos publicados quando existentes.
- **Trecho do plano**: origem, destino e valores de navegação já calculados pelo servidor.
- **Camada do mapa**: base selecionada e estados independentes das sobreposições REDEMET e RainViewer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os planos de teste, a sequência e os nomes oficiais aparecem no resumo/fichas e cada dado de aeródromo publicado aparece com contato ou indisponibilidade explícita.
- **SC-002**: Em todos os casos de limite excedido testados, o alerta aparece em vermelho e mantém texto legível sem depender da cor.
- **SC-003**: Em viewport de 1440 px, o card ocupa aproximadamente 80% da largura; em 390 px, card e controles cabem sem rolagem horizontal ou corte.
- **SC-004**: Em todos os estados testados de base e radar, a rota permanece visível, a base permanece legível e falhas não produzem substituição silenciosa.
- **SC-005**: A página não mostra “Como ler este plano” nem link de PDF no rodapé; mantém impressão no topo e o aviso didático geral.

## Assumptions

- Contatos são obtidos exclusivamente do AISWEB/ROTAER; se não forem publicados para um aeródromo, a interface indicará indisponibilidade.
- A ausência de chave Google Maps é tratada com controle desativado; a chave será configurada fora do repositório.
- A WAC permanece indisponível até validação oficial de edição, georreferenciamento, cobertura e entrega; ruas nunca serão apresentadas como carta.
- RainViewer só aparece como camada opcional separada da REDEMET e mantém avisos exigidos mesmo quando compactados.
- A largura de 80% aplica-se a telas largas; em telas menores prevalece a largura útil e a legibilidade.
