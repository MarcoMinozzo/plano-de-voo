# Feature Specification: Priorizar TAF da REDEMET

**Feature Branch**: `031-taf-redemet`

**Created**: 2026-11-27

**Status**: Draft

**Input**: User description: "pq vc nao esta incluindo o TAF do campo de marte. A redemet esta fornecendo este TAF, deveriamos usar"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar o TAF disponível da REDEMET (Priority: P1)

Como piloto, quero ver o TAF mais recente publicado pela REDEMET para o aeródromo consultado, para que uma previsão disponível não apareça como indisponível.

**Why this priority**: O usuário confirmou que a REDEMET publica o TAF de Campo de Marte e espera que o relatório aproveite esse boletim.

**Independent Test**: Simular respostas REDEMET e AWC para o mesmo aeródromo e conferir qual TAF, fonte e horários aparecem no plano e no PDF.

**Acceptance Scenarios**:

1. **Given** a REDEMET retorna um TAF válido para o aeródromo consultado, **When** o plano é exibido, **Then** o TAF REDEMET é apresentado com sua fonte e horários disponíveis.
2. **Given** a REDEMET não retorna TAF válido ou sua consulta falha, **When** o AWC retorna um TAF válido para o mesmo aeródromo, **Then** o TAF AWC continua sendo apresentado como alternativa e identificado como AWC.
3. **Given** nenhuma das fontes retorna TAF válido, **When** o plano é exibido, **Then** o TAF aparece indisponível sem reutilizar dado antigo.
4. **Given** um TAF publicado para outro indicativo, **When** o plano consulta o aeródromo atual, **Then** o boletim não é atribuído ao aeródromo consultado.
5. **Given** a consulta TAF de qualquer fonte falha, **When** o plano é exibido, **Then** METAR e os outros aeródromos permanecem disponíveis independentemente.

### Edge Cases

- REDEMET sem chave, indisponível, com resposta vazia ou malformada: consultar o AWC para o mesmo indicativo.
- Resposta com várias mensagens: selecionar a mais recente que pertença ao indicativo solicitado e contenha TAF e horários válidos.
- Mensagem sem TAF utilizável em ambas as fontes: mostrar indisponível, sem apresentar snapshot antigo como atual.
- Ausência de METAR ou falha no serviço TAF: manter o METAR válido e os boletins de outros aeródromos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Para cada aeródromo consultado na rota, o sistema MUST preferir o TAF REDEMET válido mais recente publicado para aquele mesmo indicativo.
- **FR-002**: Se a REDEMET não fornecer TAF válido ou sua consulta falhar, o sistema MUST preservar o TAF válido existente do AWC para o mesmo indicativo.
- **FR-003**: O TAF MUST permanecer associado ao indicativo consultado; o sistema MUST NOT atribuir TAF de outro aeródromo como substituto.
- **FR-004**: A tela e o PDF MUST identificar a fonte realmente utilizada para cada TAF e apresentar os horários de emissão/validade quando fornecidos.
- **FR-005**: Ausência ou falha das fontes MUST deixar o TAF afetado indisponível, sem apresentar dado antigo como atual ou inventar boletim.
- **FR-006**: Falha ou indisponibilidade de TAF MUST NOT remover METAR válido nem impedir a abertura do plano.
- **FR-007**: A chave REDEMET MUST permanecer fora da interface e das respostas públicas.
- **FR-008**: A consulta do TAF MUST NOT alterar rota, cálculos, aceitabilidade ou dados persistidos do plano.
- **FR-009**: Os boletins, fontes e estados MUST permanecer apresentados em português, preservando o aviso de uso didático.

### Key Entities

- **TAF**: Previsão textual emitida para um indicativo de aeródromo, com fonte e horários publicados.
- **Boletim meteorológico do aeródromo**: Dados METAR e TAF independentes associados ao indicativo consultado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quando REDEMET e AWC retornam TAFs válidos distintos para o mesmo indicativo, tela e PDF apresentam o TAF REDEMET.
- **SC-002**: Quando REDEMET falha ou não tem TAF válido, um TAF AWC válido continua visível com a fonte AWC identificada.
- **SC-003**: Quando nenhum provedor retorna TAF válido, o relatório mostra indisponibilidade e não exibe TAF antigo.
- **SC-004**: Em todos os cenários testados, nenhum TAF é apresentado sob um indicativo diferente daquele publicado.
- **SC-005**: O METAR válido permanece inalterado diante de qualquer falha ou indisponibilidade de TAF.

## Assumptions

- A REDEMET passa a ser a fonte prioritária de TAF; o AWC continua como alternativa para preservar a disponibilidade atual.
- A consulta é feita para cada indicativo da rota, sem fallback regional de TAF; a regra existente de METAR regional permanece inalterada.
- O boletim mais recente é determinado pelos horários publicados pela fonte e sua mensagem bruta permanece sem alterações.
- A atualização usa o fluxo atual de meteorologia ao consultar ou montar o plano e não persiste um novo snapshot durante uma consulta GET.
