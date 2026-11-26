# Feature Specification: Alinhar campos do formulário

**Feature Branch**: `026-alinhar-campos-formulario`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Junte os campos de data e número de passageiros na mesma linha e peso de pessoas e peso de bagagens na mesma linha do formulário."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preencher o formulário de voo (Priority: P1)

Como piloto, quero preencher os campos relacionados lado a lado para visualizar os dados do voo de forma mais compacta e organizada.

**Why this priority**: A disposição em pares reduz o comprimento do formulário e facilita a comparação dos valores.

**Independent Test**: Abrir o formulário de novo plano em telas largas e estreitas e verificar a disposição dos quatro campos sem alterar o envio do formulário.

**Acceptance Scenarios**:

1. **Given** o formulário em uma tela com largura de pelo menos 640 px, **When** o piloto visualiza os campos, **Then** data e número de passageiros aparecem na mesma linha.
2. **Given** o formulário em uma tela com largura de pelo menos 640 px, **When** o piloto visualiza os campos, **Then** peso das pessoas e peso da bagagem aparecem na mesma linha.
3. **Given** o formulário em uma tela com largura inferior a 640 px, **When** o piloto visualiza os campos, **Then** cada par pode empilhar verticalmente sem cortar rótulos ou controles.
4. **Given** qualquer tamanho de tela, **When** o piloto preenche e envia o formulário, **Then** os mesmos valores e validações existentes são preservados.

### Edge Cases

- Rótulos completos e unidades continuam visíveis quando os campos ficam lado a lado.
- Valores inválidos ou ausentes continuam sujeitos às validações existentes.
- Em telas estreitas, os controles não ficam comprimidos nem causam rolagem horizontal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O formulário MUST apresentar data e hora e número de passageiros lado a lado em telas com largura de pelo menos 640 px.
- **FR-002**: O formulário MUST apresentar peso das pessoas e peso da bagagem lado a lado em telas com largura de pelo menos 640 px.
- **FR-003**: Em telas com largura inferior a 640 px, os pares MUST poder ser apresentados em linhas separadas para preservar a legibilidade e o uso dos controles.
- **FR-004**: A reorganização MUST preservar rótulos, unidades, valores enviados, validações e comportamento atual do formulário.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Nas telas de pelo menos 640 px, cada par especificado ocupa uma linha compartilhada.
- **SC-002**: Em telas menores que 640 px, os quatro campos permanecem legíveis e utilizáveis sem rolagem horizontal causada pelos pares.
- **SC-003**: O envio do formulário mantém os mesmos nomes de campos, valores e validações antes e depois da reorganização.

## Assumptions

- A disposição em duas colunas é usada quando há largura suficiente; em telas menores, os campos empilham para preservar a usabilidade.
- A mudança é somente visual e não altera cálculo, persistência nem regras do plano.
