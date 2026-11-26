# Feature Specification: Aumentar logo no login

**Feature Branch**: `main`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "aumente o logo da pagina de login"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconhecer a aplicação ao entrar (Priority: P1)

Como pessoa que entra na aplicação, quero ver o logo do cartão de login um pouco maior, para reconhecê-lo com mais facilidade sem alterar o formulário.

**Why this priority**: O ajuste pedido é somente visual e afeta a leitura da página de login.

**Independent Test**: Abrir a página de entrar e comparar o tamanho e alinhamento do logo com a dimensão atual.

**Acceptance Scenarios**:

1. **Given** a página de entrar, **When** ela é exibida, **Then** o logo aparece centralizado no cartão, acima do título, 20% maior que sua largura atual de 86,4 px.
2. **Given** a página de cadastro, **When** ela é exibida, **Then** o tamanho atual do logo permanece inalterado.
3. **Given** uma página autenticada, **When** ela é exibida, **Then** o logo do cabeçalho permanece inalterado.
4. **Given** a página de entrar em viewport estreito ou largo, **When** ela é exibida, **Then** o logo mantém proporção, fica dentro do cartão e não cria rolagem horizontal.

### Edge Cases

- O logo não pode ser cortado nem empurrar campos ou botões para fora do cartão.
- A alteração não deve recolocar um logo no cabeçalho da página de entrar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A página de entrar MUST mostrar o logo 20% maior que a dimensão atual de 86,4 px, preservando a proporção da imagem.
- **FR-002**: O logo MUST permanecer centralizado no cartão e acima do título.
- **FR-003**: A mudança MUST afetar somente a página de entrar; cadastro e páginas autenticadas permanecem inalterados.
- **FR-004**: A mudança MUST preservar formulário, navegação, texto alternativo e ausência de logo no cabeçalho de entrar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A largura renderizada do logo no login corresponde a 103,68 px, 20% acima de 86,4 px.
- **SC-002**: O logo continua centralizado no cartão e visível por inteiro em viewports de 390 px e 1440 px, sem overflow horizontal.
- **SC-003**: A largura do logo em cadastro continua em 86,4 px e o cabeçalho autenticado não muda.

## Assumptions

- “Aumente” significa aumentar em 20% a dimensão atual do logo no login; a referência atual é 86,4 px.
- O pedido se limita à página de login; cadastro e páginas autenticadas não devem ser alterados.
