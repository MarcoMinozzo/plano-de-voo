# Feature Specification: Atualizar meteorologia ao consultar o plano

**Feature Branch**: `023-atualizar-meteorologia`

**Created**: 2026-11-26

**Status**: Draft

**Input**: Corrigir a ausência de dados METAR e radar meteorológico em planos existentes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar meteorologia atualizada (Priority: P1)

Como piloto, quero que METAR, TAF e radar sejam atualizados quando abro um plano, para não confundir dados antigos ou indisponíveis com as condições consultadas agora.

**Why this priority**: A página atualmente reapresenta dados gravados ao criar ou editar o plano; por isso, um plano antigo não consulta novamente as fontes.

**Independent Test**: Abrir um plano já salvo com respostas meteorológicas simuladas e confirmar que a página mostra os dados da consulta atual, não o snapshot anterior.

**Acceptance Scenarios**:

1. **Given** um plano salvo com um ou mais trechos, **When** o piloto abre a página do plano, **Then** o sistema consulta METAR/TAF dos aeródromos distintos da rota e radar para a rota antes de apresentar os dados.
2. **Given** que uma fonte retorna dados válidos, **When** o plano é exibido, **Then** os dados atuais, a fonte e o horário fornecidos aparecem identificados.
3. **Given** que o Aviation Weather Center não retorna METAR para um aeródromo, **When** o plano é exibido, **Then** aquele METAR aparece indisponível e nenhum valor antigo é apresentado como atual.
4. **Given** que a chave REDEMET não está configurada, **When** o plano é exibido, **Then** o radar aparece indisponível com o motivo explícito, sem impedir a consulta dos outros dados.
5. **Given** que METAR, TAF ou radar falha independentemente, **When** o plano é exibido, **Then** os demais dados disponíveis continuam acessíveis e a falha não altera rota ou cálculo.
6. **Given** que o piloto alterna a ficha ou a camada do mapa, **When** a interface muda de trecho ou camada, **Then** ela não inicia novas consultas meteorológicas.

### Edge Cases

- Aeródromos repetidos entre trechos são consultados uma única vez por abertura do plano.
- Uma resposta sem observação, como HTTP 204 do Aviation Weather Center, permanece indisponível; não se substitui por estação próxima ou dado estimado.
- Sem chave REDEMET, sem cobertura geográfica ou sem imagem válida, o radar permanece indisponível e desativado.
- Uma falha de uma fonte não oculta dados válidos das outras fontes nem impede abrir o plano.
- A página não apresenta snapshot antigo como se fosse uma observação atual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Ao abrir um plano salvo, o sistema MUST atualizar METAR e TAF para cada aeródromo distinto usado como origem ou destino dos trechos.
- **FR-002**: Ao abrir um plano salvo, o sistema MUST atualizar o radar para a rota quando a chave REDEMET estiver configurada.
- **FR-003**: A interface MUST identificar fonte e horário quando fornecidos pela fonte meteorológica.
- **FR-004**: A ausência de observação ou falha da fonte MUST ser indicada como indisponível; o sistema MUST NOT inventar, completar ou apresentar snapshot anterior como atual.
- **FR-005**: Radar MUST permanecer indisponível quando faltar chave, cobertura, URL ou limites geográficos válidos, com o motivo disponível ao piloto.
- **FR-006**: Uma falha de METAR, TAF ou radar MUST NOT impedir a apresentação dos dados válidos das demais fontes nem a abertura do plano.
- **FR-007**: Atualizar meteorologia MUST NOT alterar rota, cálculos, aceitabilidade, propriedade ou dados de entrada do plano.
- **FR-008**: Alternar entre fichas e camadas do mapa MUST NOT gerar novas consultas meteorológicas.
- **FR-009**: Todos os boletins e estados de disponibilidade MUST continuar apresentados em português e sem sugerir autorização operacional de voo.

### Key Entities *(include if feature involves data)*

- **Plano salvo**: Plano existente e seus trechos, cujos dados meteorológicos podem estar desatualizados.
- **Boletim meteorológico**: METAR ou TAF atual associado a um aeródromo, com texto original, fonte, horário e estado.
- **Radar de rota**: Imagem meteorológica associada à cobertura geográfica do trecho, com fonte, horário e estado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os cenários testados, abrir um plano com resposta atual disponível apresenta o METAR/TAF retornado na consulta atual, em vez de um snapshot antigo.
- **SC-002**: Em todos os cenários testados sem boletim ou sem chave REDEMET, o plano informa indisponibilidade sem inventar dados ou esconder o motivo conhecido.
- **SC-003**: Uma falha em qualquer fonte não impede apresentar dados válidos das outras fontes nem abrir o plano.
- **SC-004**: Em planos com aeródromos repetidos ou várias fichas, cada aeródromo é consultado uma vez por abertura para cada tipo de boletim e alternar fichas/camadas não faz novas consultas.
- **SC-005**: Em todos os cenários testados, a atualização meteorológica preserva os trechos, os cálculos e o estado de aceitabilidade do plano.

## Assumptions

- Aviation Weather Center continua sendo a fonte de METAR/TAF e REDEMET a fonte do radar, conforme as regras do produto.
- A chave REDEMET deve ser configurada fora do repositório; sem ela, não é possível obter radar real.
- Um aeródromo pode não ter observação METAR publicada. A ausência da observação é um estado válido e não deve ser confundida com falha do aplicativo.
- A atualização ocorre ao abrir a página do plano; alternar controles de interface não exige nova consulta.
