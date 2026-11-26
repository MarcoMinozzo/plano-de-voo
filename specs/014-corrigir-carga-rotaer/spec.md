# Feature Specification: Corrigir carga do ROTAER

**Feature Branch**: `014-corrigir-carga-rotaer`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "Faça as correções necessárias" para a falha em que `python -m servidor.catalogo` informa `ROTAER: indisponivel`, embora o AISWEB responda com dados.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carregar o catálogo ROTAER vigente (Priority: P1)

Como operador, quero carregar os aeródromos de avião da publicação vigente do ROTAER com os dados de posição e elevação publicados, para que o catálogo nacional possa ser usado pelo planejamento sem coordenadas estimadas.

**Why this priority**: Sem uma carga completa e verificável, a aplicação bloqueia planos ou corre o risco de usar dados incompletos.

**Independent Test**: Simular a resposta paginada do AISWEB e os detalhes dos aeródromos; confirmar a carga completa, a exclusão de helipontos e a origem oficial dos campos.

**Acceptance Scenarios**:

1. **Given** uma resposta AISWEB válida com aeródromos em vigor, **When** o operador carrega o catálogo, **Then** os registros de avião são carregados com identificador, nome, posição, elevação e proveniência da versão publicada.
2. **Given** páginas de aeródromos e detalhes correspondentes, **When** a carga termina, **Then** o catálogo só fica disponível depois que todos os aeródromos de avião tiverem dados completos.
3. **Given** um registro que não é aeródromo de avião, **When** a lista é carregada, **Then** ele não entra no catálogo nacional.
4. **Given** um erro HTTP, XML inválido ou detalhe obrigatório ausente, **When** a carga falha, **Then** nenhum catálogo parcial é marcado como vigente e o operador recebe um motivo sem exposição de credenciais.
5. **Given** uma atualização em que as versões publicadas não mudaram, **When** o operador carrega o catálogo novamente, **Then** detalhes já validados são reutilizados sem novas consultas individuais desnecessárias.

### Edge Cases

- O AISWEB retorna uma página vazia antes do total anunciado: a carga não termina como sucesso.
- Um aeródromo de avião não tem código ICAO ou detalhe com latitude, longitude ou elevação: a carga fica indisponível e identifica o campo ausente.
- A publicação contém helipontos ou helidecks: esses registros são excluídos sem interromper os aeródromos de avião.
- Uma resposta de detalhe não corresponde ao ICAO solicitado: o registro não é aceito.
- Uma atualização falha depois de várias páginas: dados parciais não substituem o catálogo vigente.
- A resposta de erro contém a URL da requisição: a mensagem apresentada não revela chave, senha ou parâmetros secretos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST interpretar a resposta AISWEB da lista vigente e percorrer todas as páginas anunciadas.
- **FR-002**: O catálogo nacional MUST incluir somente aeródromos de avião retornados como vigentes pela fonte oficial.
- **FR-003**: Cada aeródromo MUST ter identificador, nome, latitude, longitude, elevação e proveniência da versão publicada; nenhum campo pode ser estimado ou completado pela lista local.
- **FR-004**: O sistema MUST obter os detalhes oficiais necessários para completar os aeródromos de avião e MUST validar que cada resposta corresponde ao identificador consultado.
- **FR-005**: O catálogo MUST ser marcado disponível somente após a validação completa de todos os registros exigidos. Uma falha MUST NOT publicar um catálogo parcial.
- **FR-006**: Detalhes já validados MUST ser reutilizados quando a versão publicada correspondente não tiver mudado.
- **FR-007**: A carga MUST apresentar ao operador progresso e motivo de falha sem revelar credenciais ou parâmetros secretos da requisição.
- **FR-008**: A carga do RAB MUST continuar independente do resultado da carga ROTAER.

### Key Entities

- **Aeródromo publicado**: Registro vigente com identificador, nome, posição, elevação e versão de origem.
- **Carga do catálogo**: Execução que termina disponível apenas quando todos os registros exigidos foram validados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos aeródromos de avião retornados pela publicação vigente e elegíveis para o catálogo ficam carregados com posição, elevação e fonte verificáveis.
- **SC-002**: 100% dos helipontos e helidecks ficam fora do catálogo de aeródromos de avião.
- **SC-003**: Em qualquer falha de página ou detalhe obrigatório, 0 registros parciais são apresentados como catálogo nacional vigente.
- **SC-004**: Uma atualização sem alteração de versão reutiliza os detalhes já verificados e informa seu progresso sem exibir credenciais.

## Assumptions

- A lista AISWEB sem filtro de emenda retorna os aeródromos atualmente em vigor; cada registro inclui um identificador de versão.
- Os detalhes do aeródromo, incluindo posição e elevação, são obtidos pela consulta oficial correspondente ao ICAO.
- A API pode ficar indisponível ou limitar chamadas; nesses casos, o sistema informa a falha e não inventa nem publica dados incompletos.
- A carga do RAB permanece independente e pode concluir mesmo quando a carga do ROTAER falhar.
