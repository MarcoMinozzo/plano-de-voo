# Feature Specification: Logo centralizado no login e cadastro

**Feature Branch**: `main`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "na pagina de login e registro quero o logo dentro do card principal acima e centralizado 20% maior do que o atual . Remova o do alto da tela."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identificar a aplicação ao entrar ou criar acesso (Priority: P1)

Como pessoa que entra ou cria um acesso, quero ver o logo centralizado dentro do cartão principal, acima do título, para reconhecer a aplicação sem um logo separado no topo da tela.

**Why this priority**: O logo deve integrar visualmente as duas telas de autenticação sem distrair do formulário.

**Independent Test**: Abrir as telas de entrar e cadastro, conferir posição e dimensão do logo e verificar que ele não aparece no cabeçalho dessas telas.

**Acceptance Scenarios**:

1. **Given** a tela de entrar, **When** ela é exibida, **Then** o logo aparece centralizado no cartão, acima do título, com dimensão 20% maior que os atuais 72 px de largura.
2. **Given** a tela de cadastro, **When** ela é exibida, **Then** o logo aparece centralizado no cartão, acima do título, com a mesma dimensão da tela de entrar.
3. **Given** qualquer uma dessas telas, **When** o cabeçalho é exibido, **Then** não há um segundo logo no alto da tela.
4. **Given** uma tela autenticada, **When** ela é exibida, **Then** o logo do cabeçalho permanece como hoje.

### Edge Cases

- Em larguras estreitas e largas, o logo mantém a proporção, permanece centralizado e não causa rolagem horizontal.
- A ausência do logo no cabeçalho fica limitada às telas de entrar e cadastro; não altera formulários, navegação ou outras telas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: As telas de entrar e cadastro MUST mostrar o mesmo logo dentro do cartão principal, antes do título e centralizado horizontalmente.
- **FR-002**: O logo MUST ter largura de 86,4 px, equivalente a 20% acima dos 72 px atuais, preservando a proporção original.
- **FR-003**: O cabeçalho MUST NOT mostrar outro logo nas telas de entrar e cadastro.
- **FR-004**: O cabeçalho das telas autenticadas MUST continuar mostrando o logo atual, sem mudança.
- **FR-005**: A alteração MUST preservar o conteúdo, a navegação e o comportamento dos formulários existentes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em ambas as telas, o logo aparece uma vez dentro do cartão, acima do título e centralizado, com largura de 86,4 px.
- **SC-002**: Nenhum logo aparece no cabeçalho de entrar ou cadastro; o logo permanece no cabeçalho de uma tela autenticada.
- **SC-003**: Em viewports de 390 px e 1440 px, o logo mantém proporção e centralização sem causar overflow horizontal.

## Assumptions

- O logo existente e sua descrição acessível serão reutilizados.
- “Remova o do alto da tela” aplica-se às telas de entrar e cadastro; outras telas mantêm o cabeçalho atual.
- A largura atual de 72 px é a referência para calcular o aumento de 20%.
