# Feature Specification: Mapa quadrado com satélite REDEMET e WAC visível

**Feature Branch**: `main`

**Created**: 2026-11-27

**Status**: Draft

**Input**: User description: "Aumente o tamanho do quadro do mapa no desktop para que a altura seja a mesma da largura; adicione uma opção de imagem de satélite da REDEMET para plotar no mapa e faça a opção Carta WAC aparecer no mapa. Faça a correção rapidamente e com o mínimo de testes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar imagem de satélite (Priority: P1)

Como piloto, quero ativar a imagem de satélite REDEMET sobre o mapa do trecho para consultar as condições visuais da região sem perder a rota.

**Why this priority**: A imagem de satélite foi solicitada como uma nova camada do mapa e deve funcionar sem substituir silenciosamente o radar ou a rota.

**Independent Test**: Abrir um plano de teste, ativar e desativar a imagem com uma resposta REDEMET simulada e confirmar a fonte, o horário e a rota.

**Acceptance Scenarios**:

1. **Given** uma imagem REDEMET válida, **When** o piloto ativa Satélite, **Then** a imagem e seu horário são mostrados sobre o mapa e a rota permanece visível.
2. **Given** o satélite ativo, **When** o piloto liga ou desliga o radar, **Then** a camada de satélite permanece independente.
3. **Given** imagem, horário ou limites geográficos ausentes ou inválidos, **When** o piloto ativa Satélite, **Then** nenhuma imagem é desenhada e a indisponibilidade é informada.

### User Story 2 - Encontrar e consultar a carta WAC (Priority: P1)

Como piloto, quero encontrar sempre a opção Carta WAC no mapa e saber quando os documentos oficiais não estão disponíveis.

**Why this priority**: A opção atualmente desaparece quando o plano não tem documentos WAC válidos, embora o usuário precise saber que a carta foi verificada e está indisponível.

**Independent Test**: Abrir planos de teste com documentos AISWEB válidos e indisponíveis; confirmar que a opção está visível nos dois estados e que só o estado válido abre documentos.

**Acceptance Scenarios**:

1. **Given** documentos WAC oficiais válidos, **When** o piloto seleciona Carta WAC, **Then** os documentos são apresentados pelos links oficiais existentes.
2. **Given** nenhum documento WAC validado, **When** o piloto abre o mapa, **Then** Carta WAC permanece visível, desabilitada, e informa a indisponibilidade.
3. **Given** qualquer estado dos documentos, **When** o mapa é exibido, **Then** ruas e PDFs não são identificados como uma camada WAC georreferenciada.

### User Story 3 - Usar o mapa em telas grandes e pequenas (Priority: P2)

Como piloto, quero que o mapa aproveite melhor a tela desktop sem ficar impraticável em dispositivos pequenos.

**Why this priority**: O quadro atual é baixo em telas largas, enquanto a experiência móvel deve permanecer confortável.

**Independent Test**: Verificar a proporção do mapa em uma viewport desktop de 1440 px e a usabilidade dos controles em uma viewport móvel de 390 px.

**Acceptance Scenarios**:

1. **Given** uma tela desktop, **When** o trecho ativo é exibido, **Then** o mapa tem altura igual à largura.
2. **Given** uma tela móvel de 390 px, **When** o trecho ativo é exibido, **Then** o mapa e seus controles permanecem visíveis e utilizáveis sem alterar a navegação existente.

### Edge Cases

- A REDEMET não tem chave configurada, não responde ou retorna lista de imagens vazia.
- O frame mais recente não tem URL HTTPS válida, horário ou limites geográficos válidos.
- O plano pertence a outro piloto ou a sessão não está autenticada.
- O trecho não tem coordenadas suficientes para desenhar a rota.
- A carta WAC não tem documentos válidos; ou o documento deixa de estar acessível depois de listado.
- Satélite e radar são ativados ao mesmo tempo; ambos devem permanecer independentes, mantendo a rota legível.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O mapa MUST ter proporção 1:1 em telas desktop e continuar utilizável em telas pequenas.
- **FR-002**: O mapa MUST oferecer uma camada opcional de imagem de satélite REDEMET, desativada inicialmente e ativada somente por ação do piloto.
- **FR-003**: Quando houver imagem REDEMET válida, o sistema MUST exibir o frame mais recente com sua fonte e horário; a camada MUST ser independente do radar e não alterar os pontos da rota.
- **FR-004**: Quando a imagem, o horário ou seus limites geográficos estiverem ausentes ou inválidos, o sistema MUST deixar a camada desligada e informar a indisponibilidade sem inventar dados.
- **FR-005**: A chave REDEMET MUST permanecer no servidor e a consulta de camada MUST respeitar a propriedade do plano pelo piloto autenticado.
- **FR-006**: O controle Carta WAC MUST permanecer visível no mapa. Com documentos AISWEB válidos, deve abrir os documentos oficiais existentes; sem eles, deve ficar desabilitado e informar que a carta está indisponível.
- **FR-007**: A base de ruas e os documentos PDF MUST NOT ser apresentados como uma carta WAC georreferenciada. Uma camada raster WAC só pode ser oferecida depois dos gates de edição, georreferenciamento, cobertura e autorização previstos na feature 009.
- **FR-008**: Os controles MUST funcionar por toque e teclado, e os estados indisponíveis MUST ser acessíveis.
- **FR-009**: A interface MUST permanecer em português e preservar o aviso educacional existente.

### Key Entities

- **Frame de satélite**: Imagem REDEMET com horário, fonte e limites geográficos.
- **Documento WAC**: Carta oficial AISWEB identificada como PDF e estado disponível/indisponível.
- **Camada do mapa**: Estado de ativação de satélite e radar, independente da rota do plano.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em viewport desktop de 1440 px, a largura e a altura do quadro do mapa diferem em no máximo 1 px.
- **SC-002**: Em viewport móvel de 390 px, controles e mapa permanecem visíveis e utilizáveis sem rolagem horizontal adicional.
- **SC-003**: Em todos os casos válidos testados, a imagem REDEMET mostra fonte e horário; em todos os casos inválidos, nenhuma imagem é exibida e a indisponibilidade é comunicada.
- **SC-004**: Em todos os casos testados, a opção Carta WAC está visível; somente documentos AISWEB válidos podem ser abertos por ela.
- **SC-005**: Ativar ou desativar satélite e radar não altera os pontos da rota nem persiste uma alteração no plano.

## Assumptions

- O mapa de ruas permanece como base inicial. Satélite e radar são sobreposições opcionais e independentes, podendo ser usados ao mesmo tempo.
- A imagem exibida é o frame válido mais recente do produto REDEMET `realcada`; não será oferecida seleção de tipo ou animação nesta mudança.
- A opção WAC abre somente os documentos AISWEB atuais já fornecidos pelo plano. Esta mudança não gera nem distribui tiles WAC.
- A solicitação não inclui alterações de cálculo, persistência de planos ou dependências de runtime.
