# Feature Specification: Plano diurno e relatório organizado

**Feature Branch**: `028-plano-diurno-tabular`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Simplificar controles do mapa para uma única carta WAC e um único radar; organizar o relatório em tabelas, concentrar fontes em um modal e programar os trechos com horários diurnos, nascer/pôr do sol e pernoites."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar mapa com controles simples (Priority: P1)

Como piloto, quero ver uma base cartográfica adequada sem escolher entre provedores técnicos, para consultar a rota sem controles redundantes ou mensagens desnecessárias.

**Why this priority**: O mapa deve decidir internamente qual apresentação oficial está disponível e manter radar simples de ativar.

**Independent Test**: Abrir planos com WAC georreferenciada, somente PDF oficial e sem carta disponível; ativar o radar em cenários com REDEMET, RainViewer ou ambas as fontes.

**Acceptance Scenarios**:

1. **Given** uma WAC vigente, validada e georreferenciada, **When** o piloto abre o mapa, **Then** a carta é usada como base e há no máximo um controle de mapa identificado como “Carta WAC”.
2. **Given** uma ou mais WACs oficiais disponíveis somente em PDF, **When** o piloto aciona “Carta WAC”, **Then** os PDFs oficiais correspondentes à rota são abertos ou listados em ordem de trecho, sem serem apresentados como uma camada georreferenciada.
3. **Given** nenhuma WAC utilizável, **When** o piloto abre o mapa, **Then** o mapa de ruas permanece como base, o controle WAC não é exibido e não há mensagem visual redundante de indisponibilidade.
4. **Given** qualquer estado dos provedores de radar, **When** o piloto usa o mapa, **Then** há somente um controle “Radar de chuva”; a REDEMET tem prioridade e RainViewer pode ser escolhida automaticamente se a REDEMET estiver indisponível.
5. **Given** RainViewer selecionada, **When** o radar aparece, **Then** a fonte ativa, o crédito vinculado, o horário do frame e o aviso de cobertura continuam visíveis, sem apresentá-la como fonte oficial.
6. **Given** uma tela estreita, **When** o piloto abre e usa o mapa, **Then** rota, mapa e controles cabem na largura útil e permanecem operáveis por toque e teclado.

---

### User Story 2 - Ler o relatório e consultar fontes (Priority: P1)

Como piloto, quero localizar os dados do plano em tabelas e consultar a procedência sem interromper a leitura de cada trecho.

**Why this priority**: Um relatório tabular reduz repetição e permite consultar fontes sob demanda sem remover a rastreabilidade.

**Independent Test**: Abrir um plano com valores de navegação, meteorologia, aeródromos e aeronave; conferir as tabelas, abrir o modal de fontes e usar a impressão.

**Acceptance Scenarios**:

1. **Given** um plano com dados disponíveis, **When** o piloto abre o relatório, **Then** as informações relacionadas aparecem agrupadas em tabelas claras e responsivas.
2. **Given** o relatório aberto, **When** o piloto aciona o ícone “i” ao lado da impressão, **Then** um modal apresenta uma tabela que associa cada campo à sua fonte e metadados disponíveis.
3. **Given** o relatório ou a impressão, **When** valores são apresentados, **Then** as fontes não interrompem o corpo do relatório; a rastreabilidade aparece no modal e em uma seção de fontes separada na impressão.
4. **Given** a tela de impressão, **When** o piloto a abre, **Then** a ação de imprimir permanece no topo junto ao ícone de informações.

---

### User Story 3 - Planejar trechos dentro do período diurno (Priority: P1)

Como piloto, quero ver os horários estimados de cada trecho e os limites de luz do dia, para identificar escalas e pernoites na sequência planejada.

**Why this priority**: A ficha já estima duração e rota, mas precisa tornar explícitos os horários e impedir que uma programação seja apresentada como diurna quando ultrapassa o pôr do sol.

**Independent Test**: Planejar rotas de um e vários trechos em dias com diferentes horários solares; conferir ETD, ETA, nascer/pôr do sol, adiamentos para o dia seguinte e pernoites.

**Acceptance Scenarios**:

1. **Given** um plano com trechos, **When** o piloto consulta cada trecho, **Then** vê data e hora estimadas de partida (ETD) e chegada (ETA), além do nascer e pôr do sol relevantes.
2. **Given** uma partida ou chegada estimada depois do pôr do sol, **When** a sequência é programada, **Then** o trecho é movido para o próximo nascer do sol disponível e o relatório identifica o pernoite no aeródromo de partida desse trecho.
3. **Given** dados solares indisponíveis ou inválidos para um aeródromo e uma data, **When** o plano é calculado, **Then** o horário solar não é inventado e a programação não é declarada como compatível com o período diurno.
4. **Given** um trecho que não cabe entre o nascer e o pôr do sol mesmo após adiamento, **When** o servidor calcula a sequência, **Then** o trecho não é apresentado como programável naquele aeródromo sem escala adicional.
5. **Given** uma rota com mais de um dia, **When** o relatório é exibido ou impresso, **Then** as datas dos trechos e os locais de pernoite aparecem na ordem correta.

### Edge Cases

- Se não houver WAC georreferenciada, mas houver PDF oficial, o PDF pode ser aberto sem ser sobreposto ao mapa nem descrito como georreferenciado.
- Se não houver WAC ou link oficial, o mapa de ruas permanece; não é apresentado como carta aeronáutica.
- Se REDEMET e RainViewer estiverem indisponíveis, o único controle de radar fica indisponível sem mensagens de configuração específicas por provedor.
- Se RainViewer for selecionada, seus termos, cobertura, tiles, horário e crédito precisam estar válidos; caso contrário, nenhum radar é exibido.
- Se o modal de fontes não tiver metadados para um campo, esse campo permanece identificado como fonte indisponível, sem fabricar publicador ou data.
- Se o horário estimado coincidir com o pôr do sol, a comparação usa o instante fornecido pela fonte e não aplica margem operacional não especificada.
- Se faltar nascer ou pôr do sol em qualquer aeródromo/data necessário à programação, o servidor não presume que a perna caiba no período diurno.
- Se um trecho não couber no período diurno em nenhum dos dias programáveis, o sistema informa a programação indisponível em vez de repetir adiamentos indefinidamente.
- Uma sequência de vários trechos pode exigir mais de um pernoite; cada adiamento permanece associado ao aeródromo onde a próxima perna aguardará.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O mapa MUST apresentar no máximo um controle de base com o rótulo “Carta WAC” e no máximo um controle “Radar de chuva”; MUST NOT apresentar controles Google Maps, OpenAIP ou mapa de ruas separado.
- **FR-002**: Quando houver WAC oficial vigente, validada e georreferenciada para a rota, o mapa MUST poder apresentá-la; quando houver apenas PDF oficial, o único controle “Carta WAC” MUST abrir ou listar os PDFs oficiais correspondentes à rota, em ordem de trecho, sem tratá-los como camada geográfica.
- **FR-003**: Quando não houver WAC utilizável, o mapa MUST permanecer sobre a base de ruas, MUST NOT rotulá-la como carta aeronáutica e MUST NOT imprimir ou exibir as mensagens “Carta WAC indisponível — validação pendente.”, “Chave REDEMET não configurada” ou “Mapa de ruas; não substitui a carta de voo visual oficial.”. A indisponibilidade MUST continuar perceptível por estado acessível não visual quando necessário.
- **FR-004**: O mapa MUST oferecer no máximo um controle “Radar de chuva”. O servidor MUST priorizar REDEMET e MAY selecionar RainViewer automaticamente quando REDEMET estiver indisponível, conforme a constituição.
- **FR-005**: Quando RainViewer for a fonte ativa, a interface MUST identificar a fonte real, exibir o crédito com link, o horário informado e a ressalva de cobertura; MUST NOT apresentá-la como radar oficial ou como REDEMET.
- **FR-006**: Quando nenhuma fonte de radar for elegível, o radar MUST permanecer sem imagem e o estado acessível do controle único MUST indicar indisponibilidade sem mensagem visual de chave ausente ou detalhes de configuração.
- **FR-007**: O mapa e seus controles MUST adaptar-se a telas pequenas sem corte, sobreposição ou rolagem horizontal, mantendo uso por toque e teclado.
- **FR-008**: O relatório MUST agrupar informações relacionadas em tabelas organizadas; em telas estreitas, a leitura MUST permanecer possível sem rolagem horizontal global.
- **FR-009**: O relatório MUST evitar citações de fonte repetidas junto a cada valor no corpo principal.
- **FR-010**: Um ícone “i” MUST aparecer ao lado da ação de impressão no topo e abrir um modal acessível com uma tabela que relacione campo e fonte, incluindo publicador, referência, data, unidade e aplicabilidade quando esses dados existirem.
- **FR-011**: A impressão MUST manter as fontes fora do corpo principal e incluí-las em uma seção separada de procedência, preservando a rastreabilidade exigida.
- **FR-012**: Cada trecho MUST apresentar ETD e ETA estimadas, incluindo data e horário em UTC, e MUST identificar o nascer e o pôr do sol aplicáveis à partida e à chegada.
- **FR-013**: O servidor MUST impedir que uma programação aceite uma partida ou chegada após o pôr do sol informado pela fonte oficial.
- **FR-014**: Quando uma perna não puder partir e chegar dentro do período diurno, o servidor MUST adiá-la para o próximo nascer do sol disponível no aeródromo de partida e MUST registrar pernoite nesse aeródromo.
- **FR-015**: O servidor MUST calcular a sequência de várias pernas e dias sem permitir chegadas após o pôr do sol; MUST indicar indisponibilidade quando dados solares necessários estiverem ausentes ou uma perna não couber no período diurno.
- **FR-016**: O nascer e o pôr do sol MUST ser obtidos da área solar oficial do AISWEB para o indicador do aeródromo e a data correspondente. Ausências ou respostas inválidas MUST permanecer indisponíveis, sem cálculo substituto ou valor inventado.
- **FR-017**: Cálculos de duração, horários, escalas, datas e pernoites MUST ocorrer no servidor; a interface MUST apenas apresentar os valores recebidos.
- **FR-018**: A mudança MUST preservar autorização por piloto, dados originais do plano, aviso didático e a distinção entre carta oficial, base de ruas e fonte ativa do radar.
- **FR-019**: O primeiro cartão do relatório MUST apresentar a rota completa, da origem ao destino, como sequência ordenada de trechos.
- **FR-020**: Cada trecho MUST exibir o nome completo dos aeródromos de origem e destino; os contatos verificados de origem e destino MUST ser apresentados quando disponíveis, sem inventar dados ausentes. Os códigos ICAO podem permanecer nos títulos e nas abas.
- **FR-021**: Excesso de peso ou valores fora dos limites MUST gerar avisos destacados em vermelho, com texto que identifique o problema sem depender somente da cor.
- **FR-022**: Em telas largas, o cartão principal MUST ocupar aproximadamente 80% da largura útil; em telas estreitas, MUST adaptar-se à largura disponível sem rolagem horizontal global.
- **FR-023**: O relatório MUST NOT repetir a seção “Como ler este plano” nem colocar uma segunda ação de impressão no fim da página; a impressão permanece no topo junto ao ícone de fontes.

### Key Entities

- **Trecho programado**: origem, destino, duração estimada, ETD, ETA, data, estado diurno e eventual pernoite associado.
- **Condição solar**: aeródromo, data, nascer do sol, pôr do sol, fonte e estado de disponibilidade.
- **Fonte de relatório**: campo, publicador, referência, data e aplicabilidade exibidos sob demanda e na seção de procedência da impressão.
- **Camada do mapa**: apresentação WAC ou base de ruas, selecionada conforme disponibilidade oficial.
- **Radar de chuva**: uma camada controlada pelo piloto, com provedor selecionado conforme prioridade e disponibilidade, mantendo a identidade da fonte ativa.
- **Dados do aeródromo**: nome completo, código ICAO e contatos verificados publicados no ROTAER, quando disponíveis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os cenários testados, o mapa apresenta no máximo um controle de WAC e um controle de radar, sem botão Google Maps/OpenAIP ou controle separado de ruas.
- **SC-002**: Em todos os cenários de carta, uma WAC válida é exibida ou aberta como PDF oficial conforme sua disponibilidade; sem WAC, o mapa permanece em ruas sem mensagem redundante.
- **SC-003**: Em 390 px e 1440 px, o mapa, a rota e os controles permanecem utilizáveis, sem rolagem horizontal global ou corte dos controles.
- **SC-004**: Em todos os cenários de radar, REDEMET tem prioridade; RainViewer só aparece como alternativa identificada, com crédito e horário, e nenhum radar sem fonte válida é desenhado.
- **SC-005**: Em todos os planos de teste, cada trecho mostra ETD, ETA, nascer e pôr do sol aplicáveis ou marca explicitamente a programação como indisponível quando os dados faltam.
- **SC-006**: Nenhuma programação aceita contém ETD ou ETA após o pôr do sol; todo adiamento para outro dia identifica a data e o aeródromo do pernoite.
- **SC-007**: Em todos os campos testados, o modal de fontes relaciona campo e fonte; a impressão mantém essa relação em seção separada, sem citações repetidas no corpo principal.
- **SC-008**: Todas as decisões de horário e remarcação são reproduzíveis no servidor e a interface não recalcula os valores.

## Assumptions

- Os horários de partida, chegada, nascer e pôr do sol são exibidos em UTC, seguindo a convenção dos dados AISWEB.
- O horário estimado de cada trecho usa a duração de voo já calculada; não é adicionado tempo de solo ou abastecimento não informado.
- Quando uma perna precisa ser adiada, a próxima tentativa ocorre no nascer do sol seguinte disponível no aeródromo de partida; esse aeródromo é o local do pernoite.
- A aplicação usa REDEMET como prioridade e RainViewer como alternativa automática somente com identificação e atribuição visíveis no mapa.
- A WAC só é desenhada como mapa se a georreferência e cobertura estiverem validadas; o PDF oficial pode ser aberto como documento separado.
- O mapa de ruas é o fallback cartográfico quando não houver uma WAC utilizável; não é apresentado como carta aeronáutica.
- Fontes relacionadas a valores continuam acessíveis no modal e na seção de procedência da impressão, embora não apareçam repetidamente junto aos valores do corpo principal.
