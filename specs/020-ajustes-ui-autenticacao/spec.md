# Feature Specification: Aprimorar cartões de autenticação

**Feature Branch**: `main`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "O logo no card de login e registro deve ser 50% maior; remova a palavra Entrar; abaixo do criar acesso crie uma frase em fontes pequenas e em branco - Sistema Desenvolvido por Machina Sapiens - Todos os Direitos Reservados - 2026; centralize o card na tela na vertical e horizontal; aumente o espaço entre a caixa de senha e o botão Acessar para ficar mais harmônico."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Acessar e criar uma conta com cartões equilibrados (Priority: P1)

Como pessoa que entra ou cria acesso, quero cartões de autenticação centralizados, com o logo em destaque e espaçamento confortável, para reconhecer a aplicação e usar os formulários com clareza.

**Why this priority**: Entrar e criar acesso são os principais pontos de entrada da aplicação.

**Independent Test**: Abrir `/entrar` e `/cadastro`, conferir os logos e a posição dos cartões em viewports móveis e desktop, e validar que os formulários continuam utilizáveis.

**Acceptance Scenarios**:

1. **Given** a tela de login, **When** o cartão é exibido, **Then** o logo mede 155,52 px, o título visível “Entrar” não aparece e o botão de envio se chama “Acessar”.
2. **Given** o formulário de login, **When** seus controles são exibidos, **Then** o espaço entre a senha e “Acessar” é aproximadamente o dobro do espaço normal entre controles adjacentes.
3. **Given** a tela de login, **When** o link “Criar acesso” é exibido, **Then** logo abaixo aparece “Sistema Desenvolvido por Machina Sapiens - Todos os Direitos Reservados - 2026” em branco e fonte pequena.
4. **Given** a tela de cadastro, **When** o cartão é exibido, **Then** o logo mede 129,6 px e o cartão fica centralizado na viewport.
5. **Given** uma viewport móvel ou desktop, **When** qualquer cartão é exibido, **Then** ele fica centralizado horizontal e verticalmente, sem rolagem horizontal, e seus campos e ações permanecem acessíveis.

### Edge Cases

- Se a altura da viewport não comportar o cartão, o conteúdo permanece acessível por rolagem vertical, sem corte de campos ou botões.
- Mensagens de validação não podem esconder controles nem impedir o envio dos formulários.
- O aumento do logo preserva sua proporção, texto alternativo e presença única dentro dos cartões.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O logo do cartão de login MUST ter largura de 155,52 px, 50% maior que sua largura atual de 103,68 px, mantendo proporção.
- **FR-002**: O logo do cartão de cadastro MUST ter largura de 129,6 px, 50% maior que sua largura atual de 86,4 px, mantendo proporção.
- **FR-003**: A tela de login MUST ocultar o título visível “Entrar” e identificar o botão de envio como “Acessar”, sem alterar o destino ou funcionamento do formulário.
- **FR-004**: A tela de login MUST mostrar abaixo do link “Criar acesso” a frase “Sistema Desenvolvido por Machina Sapiens - Todos os Direitos Reservados - 2026”, em branco e menor que o texto do link.
- **FR-005**: Os cartões de login e cadastro MUST ficar centralizados horizontal e verticalmente na área visível da tela.
- **FR-006**: O espaço entre o campo de senha e o botão “Acessar” MUST ser aproximadamente duas vezes o intervalo normal entre controles adjacentes do formulário.
- **FR-007**: Campos, rótulos, validação, links, envio dos formulários, texto alternativo do logo e acessibilidade MUST ser preservados.
- **FR-008**: O layout MUST evitar rolagem horizontal e manter os controles acessíveis em telas móveis e desktop; quando a altura for insuficiente, MAY usar rolagem vertical.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O logo renderizado mede 155,52 px no login e 129,6 px no cadastro, sem distorção.
- **SC-002**: Em viewports de 390 px e 1440 px de largura, o centro de cada cartão fica alinhado ao centro da área de conteúdo, sem overflow horizontal.
- **SC-003**: Na tela de login, o botão “Acessar” continua enviando o formulário e o título “Entrar” não aparece no cartão.
- **SC-004**: O espaço entre senha e “Acessar” é aproximadamente o dobro do intervalo entre os demais controles adjacentes.
- **SC-005**: A frase de autoria aparece uma vez, abaixo de “Criar acesso”, em branco e menor que o link.

## Assumptions

- As dimensões de referência são as atuais: 103,68 px no login e 86,4 px no cadastro.
- “Remova a palavra Entrar” significa remover o título visível do cartão e renomear o botão para “Acessar”; o título da aba do navegador não faz parte deste ajuste.
- A frase de autoria é exibida somente no cartão de login, abaixo do link “Criar acesso”.
- Em viewports de altura reduzida, manter os controles acessíveis por rolagem vertical tem prioridade sobre centralização vertical estrita.
