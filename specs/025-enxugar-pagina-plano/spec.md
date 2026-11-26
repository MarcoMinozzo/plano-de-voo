# Feature Specification: Enxugar informações da página do plano

**Feature Branch**: `025-enxugar-pagina-plano`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Na página do plano de voo remova o estado aceitável para planejamento, o aviso extenso e alvo de exercício do perfil sintético, a hipótese de reabastecimento em escalas e a tabela Fontes técnicas da aeronave."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar um plano sem informações repetitivas (Priority: P1)

Como piloto, quero ver a rota e os dados essenciais do plano sem avisos extensos e tabelas de proveniência repetidas, para localizar rapidamente as informações relevantes.

**Why this priority**: O excesso de mensagens e colunas técnicas aumenta o ruído visual na página do plano.

**Independent Test**: Abrir um plano de perfil sintético com escala e confirmar que os textos e a tabela indicados foram removidos, enquanto o aviso didático geral e os dados operacionais do plano permanecem.

**Acceptance Scenarios**:

1. **Given** um plano de perfil sintético, **When** o piloto abre a página, **Then** não aparecem o aviso sintético extenso, o alvo do exercício nem a tabela "Fontes técnicas da aeronave", e o aviso geral didático permanece.
2. **Given** um plano com escalas, **When** o piloto consulta a página, **Then** não aparece a hipótese textual de reabastecimento.
3. **Given** um plano, **When** o piloto consulta a página, **Then** não aparece o campo "Estado: aceitável para planejamento", mas motivos e alertas relevantes continuam visíveis.
4. **Given** um plano impresso em PDF, **When** o piloto abre o documento, **Then** seu conteúdo permanece inalterado por esta limpeza da página.

### Edge Cases

- Planos sem escala ou sem dados de proveniência continuam sendo renderizados normalmente.
- Planos não sintéticos mantêm suas estimativas, alertas e avisos gerais existentes.
- A remoção de apresentação não altera resultado, fonte, dados persistidos, cálculo ou PDF.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A página do plano MUST omitir o texto de estado "aceitável para planejamento", sem ocultar motivo de inviabilidade ou alertas.
- **FR-002**: A página do plano MUST omitir o aviso extenso de perfil sintético e a identificação do alvo do exercício.
- **FR-003**: A página do plano MUST omitir a hipótese textual de reabastecimento em cada escala.
- **FR-004**: A página do plano MUST omitir integralmente a seção e a tabela "Fontes técnicas da aeronave".
- **FR-005**: A página MUST manter o aviso geral de uso exclusivamente didático e de que o resultado não autoriza voo.
- **FR-006**: Esta mudança MUST NOT alterar os cálculos, resultados persistidos, fontes técnicas ou conteúdo do PDF.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os planos de teste, nenhum dos quatro blocos especificados para remoção é renderizado na página.
- **SC-002**: O aviso geral didático e os motivos/alertas relevantes continuam presentes quando aplicáveis.
- **SC-003**: Os dados do plano e o PDF permanecem idênticos antes e depois da limpeza visual.

## Assumptions

- O escopo se limita à página HTML de detalhes do plano; o PDF e os dados armazenados não mudam.
- A página mantém o aviso geral exigido pela constituição, mesmo removendo os rótulos extensos específicos de perfil sintético.
