# Feature Specification: Redesenho do menu principal

**Feature Branch**: `main`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Refaça o menu principal: logo 50% maior, fora da barra; substitua a barra por um card azul semitransparente centralizado que ocupe 70% da tela; menus NOVO VOO, VOOS PLANEJADOS, PERFIL e SAIR; coloque IMPRIMIR VOO dentro do primeiro card do voo planejado."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegar e imprimir um plano (Priority: P1)

Como pessoa autenticada, quero um menu principal destacado e organizado, com a impressão disponível dentro do resumo do voo, para acessar as áreas da aplicação e imprimir o plano sem uma ação duplicada na navegação global.

**Why this priority**: O menu é o ponto de acesso comum às principais funções; imprimir é uma ação específica de um voo planejado.

**Independent Test**: Abrir páginas autenticadas e um plano individual; verificar o logo, a barra, os quatro itens globais e a ação de impressão no primeiro card do plano.

**Acceptance Scenarios**:

1. **Given** uma página autenticada, **When** o menu principal aparece, **Then** o logo está fora e ao lado do card de navegação, com largura 50% maior que a atual.
2. **Given** uma página autenticada, **When** o menu principal aparece, **Then** um card azul semitransparente ocupa 70% da largura da tela e fica centralizado; seus itens são “NOVO VOO”, “VOOS PLANEJADOS”, “PERFIL” e “SAIR”.
3. **Given** uma tela estreita, **When** os itens não couberem em uma linha, **Then** eles podem quebrar linha sem sobreposição ou rolagem horizontal.
4. **Given** a página de um voo planejado, **When** o primeiro card de resumo é exibido, **Then** “IMPRIMIR VOO” aparece dentro dele e gera o PDF daquele voo.
5. **Given** qualquer página autenticada, **When** a navegação global aparece, **Then** não há item “IMPRIMIR VOO” no menu principal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O logo do menu principal MUST manter sua proporção, aumentar 50% em relação à largura atual de 72 px e permanecer fora do card de navegação.
- **FR-002**: O menu principal MUST ser apresentado em um card semitransparente no mesmo tom azul dos cards existentes, com largura de 70% da viewport e alinhamento horizontal central.
- **FR-003**: O card MUST apresentar os itens “NOVO VOO”, “VOOS PLANEJADOS”, “PERFIL” e “SAIR”, mantendo as rotas e o envio POST de saída existentes.
- **FR-004**: “IMPRIMIR VOO” MUST deixar de aparecer na navegação global e aparecer dentro do primeiro card de resumo da página individual do voo planejado, apontando para o PDF desse plano.
- **FR-005**: Em viewports estreitas, os itens do menu MAY quebrar linha, sem sobreposição nem rolagem horizontal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O logo renderizado mede 108 px de largura, mantém sua proporção e fica visualmente fora do card do menu.
- **SC-002**: Em viewport desktop de 1440 px, o card de navegação mede 70% da largura da viewport e seu centro horizontal coincide com o centro da viewport.
- **SC-003**: Em viewports de 390 px e 1440 px, os quatro itens de navegação permanecem visíveis e operáveis sem rolagem horizontal.
- **SC-004**: Na página de um plano, existe uma ação de impressão no primeiro card de resumo e ela leva ao PDF correspondente; a navegação global não contém essa ação.

## Assumptions

- O logo atual tem 72 px de largura; o novo tamanho será 108 px.
- O card do voo planejado refere-se ao primeiro card de resumo na página individual `/planos/<id>`.
- A largura solicitada de 70% aplica-se ao card de navegação; em telas estreitas, os itens podem ocupar mais de uma linha.
- A semitransparência e a cor usarão o mesmo azul dos cards de vidro existentes.
