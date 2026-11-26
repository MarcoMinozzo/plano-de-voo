# Feature Specification: Refinamento do menu e horários

**Feature Branch**: `022-refinamento-menu-horarios`

**Created**: 2026-11-26

**Status**: Draft

**Input**: Refinar a experiência do menu principal autenticado e a leitura do horário nos planos.

## User Scenarios & Testing

### User Story 1 - Navegar com clareza (Priority: P1)

Como piloto, quero um cabeçalho organizado em telas grandes e pequenas para encontrar as áreas principais sem esforço.

**Why this priority**: O menu é usado em todas as telas autenticadas e precisa funcionar também em dispositivos estreitos.

**Independent Test**: Abrir uma tela autenticada em 1440 px e 390 px, navegar por teclado e toque e verificar rótulos, ícones e alinhamento.

**Acceptance Scenarios**:

1. **Given** uma tela autenticada larga, **When** o cabeçalho aparece, **Then** o logo e o centro do card de navegação ficam alinhados verticalmente, o menu fica centralizado na página e sua largura acompanha o conteúdo com margens internas equilibradas.
2. **Given** qualquer tela autenticada, **When** o menu aparece, **Then** Novo voo, Voos planejados e Perfil têm ícones coerentes, tipografia uniforme e texto em cinza muito claro; Sair é representado apenas por ícone e mantém a ação de saída.
3. **Given** uma tela estreita, **When** o cabeçalho aparece, **Then** o menu é recolhido em um botão sanduíche acessível e pode ser aberto sem causar rolagem horizontal.
4. **Given** qualquer cartão azul da interface, **When** ele é exibido, **Then** usa um azul translúcido com aparência mais marinho e menos acinzentada.

### User Story 2 - Ler o horário de partida (Priority: P1)

Como piloto, quero ler o horário de partida até os minutos e saber que ele representa tempo local.

**Why this priority**: Segundos e frações não ajudam a leitura do horário apresentado no plano.

**Independent Test**: Abrir o painel com um plano e conferir que o horário não exibe segundos e termina em “TL”.

**Acceptance Scenarios**:

1. **Given** um plano listado, **When** seu horário de partida aparece, **Then** a data e o horário aparecem até os minutos, seguidos de “TL”.

## Edge Cases

- Em telas estreitas, o menu aberto continua dentro da largura visível e seus controles permanecem operáveis.
- A ação Sair mantém seu nome acessível mesmo sem texto visível.

## Requirements

### Functional Requirements

- **FR-001**: O logo autenticado MUST ter aproximadamente 140 px de largura, preservar a proporção e manter espaçamento lateral confortável.
- **FR-002**: O centro vertical do logo MUST coincidir com o centro vertical do card de navegação.
- **FR-003**: O card do menu MUST ser centralizado horizontalmente, ajustar sua largura ao conjunto dos itens e incluir espaço equilibrado antes do primeiro e depois do último item.
- **FR-004**: Novo voo, Voos planejados e Perfil MUST exibir ícones ao lado dos rótulos; os rótulos MUST usar tamanho e peso tipográfico uniformes.
- **FR-005**: Sair MUST exibir somente um ícone, conservar nome acessível e continuar executando a saída existente.
- **FR-006**: Em telas estreitas, a navegação MUST usar um menu sanduíche operável por teclado e toque.
- **FR-007**: Texto atualmente branco MUST usar tom próximo de branco com cerca de 5% de cinza; cartões azuis MUST adotar um tom mais marinho e menos acinzentado, mantendo translucidez.
- **FR-008**: O horário de partida listado MUST exibir data e hora até minutos, sem segundos, e terminar com “TL”.
- **FR-009**: Os controles, destinos e método da navegação existente MUST permanecer preservados.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Em viewport de 1440 px, o centro horizontal do menu coincide com o centro da página e o centro vertical do logo com o do card, com tolerância visual de 1 px.
- **SC-002**: Em viewports de 390 px e 1440 px, os controles de navegação permanecem visíveis ou acessíveis pelo menu, sem rolagem horizontal.
- **SC-003**: A largura renderizada do logo autenticado é aproximadamente 140 px.
- **SC-004**: Todo horário de partida exibido termina em “TL” e não contém segundos.
- **SC-005**: Todos os rótulos visíveis do menu usam tamanho e peso uniformes; o controle Sair não exibe texto.

## Assumptions

- O aumento de 30% é aplicado à largura autenticada atual de 108 px, resultando em aproximadamente 140 px.
- “Ícone ao lado do nome no menu” significa um ícone coerente para cada item que exibe texto.
- A hora será apresentada no valor já registrado, sem alterar cálculos ou conversões existentes; “TL” apenas identifica a indicação solicitada.
- O menu sanduíche será usado em telas estreitas; o menu amplo permanece como navegação central em telas maiores.
