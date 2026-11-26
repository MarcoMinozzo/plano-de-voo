# Feature Specification: Filtro integrado na seleção de aeródromos

**Feature Branch**: `012-filtro-integrado-aerodromos`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "Na página de inclusão da rota, não quero campo de filtro para o aeroporto de origem e destino. Quero que o mesmo campo onde tenha a seleção da origem e destino sirva também de filtro ao digitarmos parte do nome."

## User Scenarios & Testing

### User Story 1 - Selecionar aeródromos pelo próprio campo (Priority: P1)

Como piloto, quero localizar e escolher origem e destino no mesmo campo, para não precisar preencher filtros separados.

**Why this priority**: Reduz campos redundantes e torna a seleção de aeródromos mais direta.

**Independent Test**: Abrir a inclusão de plano, pesquisar por parte do nome e do código em origem e destino, escolher resultados e enviar o formulário.

**Acceptance Scenarios**:

1. **Given** a tela de novo plano, **When** o piloto digita parte do nome ou código no campo de origem ou destino, **Then** as opções correspondentes são filtradas nesse mesmo campo, sem campos de filtro separados.
2. **Given** opções filtradas, **When** o piloto escolhe um aeródromo, **Then** o campo mostra o aeródromo escolhido e o formulário envia seu identificador publicado.
3. **Given** que o piloto digitou texto sem escolher uma opção, **When** tenta enviar o formulário, **Then** a entrada não é aceita como aeródromo selecionado e o campo informa que uma opção deve ser escolhida.
4. **Given** uma resposta de validação do formulário, **When** a tela é exibida novamente, **Then** origem e destino previamente escolhidos permanecem selecionados.

### Edge Cases

- Busca vazia: opções disponíveis podem ser consultadas sem descartar a seleção vigente até o piloto começar a editar.
- Busca sem correspondência: informar que nenhum aeródromo foi encontrado e impedir texto livre de ser enviado como seleção.
- Busca ignora maiúsculas, minúsculas e acentos e encontra correspondências parciais no código ou no nome.
- Navegação por teclado permite percorrer opções, confirmar uma opção e fechar a lista sem seleção.

## Requirements

### Functional Requirements

- **FR-001**: Para origem e destino, o sistema MUST apresentar um único campo visível que permita pesquisar e selecionar; MUST NOT apresentar campos de filtro separados.
- **FR-002**: O campo MUST filtrar por trecho do código ou do nome, sem diferenciar caixa ou acentuação.
- **FR-003**: O formulário MUST enviar o identificador do aeródromo selecionado, não o texto parcial digitado.
- **FR-004**: Texto digitado sem uma opção escolhida MUST ser recusado antes do envio como seleção válida.
- **FR-005**: A seleção MUST funcionar com teclado e tecnologias assistivas, mantendo rótulos, foco e estado da lista acessíveis.
- **FR-006**: Valores selecionados MUST permanecer visíveis quando uma resposta de validação reapresentar o formulário.
- **FR-007**: A mudança MUST NOT alterar catálogo, validação do servidor, dados persistidos ou cálculo de rota.
- **FR-008**: Sem JavaScript, origem e destino MUST continuar selecionáveis pelos controles nativos do navegador.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Em todos os testes de tela, há um campo visível por origem e destino e nenhum campo separado de filtro.
- **SC-002**: Em todos os testes de busca, consultas por trecho de nome ou código, com variações de caixa e acento, retornam as opções correspondentes.
- **SC-003**: Em todos os testes de envio, somente a opção escolhida resulta no identificador do aeródromo enviado; texto livre não é enviado como seleção válida.
- **SC-004**: Os testes de navegação por teclado confirmam opção, fecham a lista e mantêm o foco sem perder a seleção.
- **SC-005**: Sem JavaScript, os controles nativos continuam permitindo selecionar e enviar origem e destino.

## Assumptions

- A busca usa o catálogo de aeródromos já fornecido à tela; não requer chamadas de rede adicionais.
- O filtro funciona tanto para catálogos locais quanto nacionais e não muda a regra que identifica a origem oficial dos dados.
- A interface permanece em português e segue a casca visual existente.
