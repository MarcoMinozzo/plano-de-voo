# Feature Specification: Camada suplementar de radar RainViewer

**Feature Branch**: `024-camada-radar-rainviewer`

**Created**: 2026-11-26

**Status**: Draft

**Input**: Decisão do usuário: adicionar RainViewer como camada opcional e não oficial, mantendo a REDEMET separada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar radar suplementar (Priority: P1)

Como piloto, quero ativar uma camada RainViewer separada do radar oficial da REDEMET, para consultar uma fonte alternativa sem confundi-la com dado oficial nem depender de uma chave REDEMET.

**Why this priority**: O usuário relatou que já visualizou radar sem chave e quer uma fonte alternativa. A camada suplementar pode ampliar a disponibilidade visual sem substituir a fonte oficial nem ocultar sua indisponibilidade.

**Independent Test**: Abrir um plano com resposta RainViewer simulada e confirmar que o piloto pode ativar a camada, identificar a fonte e o horário, manter a rota e a base selecionada e continuar vendo o estado independente da REDEMET.

**Acceptance Scenarios**:

1. **Given** um plano aberto e RainViewer disponível, **When** o piloto ativa sua camada, **Then** os dados de radar aparecem como fonte suplementar não oficial, com crédito e link visíveis.
2. **Given** RainViewer indisponível ou sem cobertura para a área exibida, **When** o piloto abre ou tenta ativar a camada, **Then** a interface informa indisponibilidade e não apresenta outra fonte como se fosse RainViewer.
3. **Given** REDEMET indisponível e RainViewer disponível, **When** o piloto ativa RainViewer, **Then** a camada RainViewer funciona sem alterar nem ocultar o estado de indisponibilidade da REDEMET.
4. **Given** RainViewer indisponível e REDEMET disponível, **When** o piloto consulta o mapa, **Then** somente a camada REDEMET pode ser ativada e nenhum fallback automático ocorre.
5. **Given** uma base cartográfica e uma rota visíveis, **When** o piloto alterna a camada RainViewer, **Then** a base, a rota, o zoom e os cálculos do plano permanecem inalterados.

### Edge Cases

- O serviço não entrega frames recentes, tiles válidos ou cobertura para a região do plano.
- A máscara de cobertura está ausente, inválida ou não pode distinguir uma área sem radar de uma área sem eco.
- O manifesto ou uma imagem retorna erro, timeout ou formato inválido.
- O serviço deixa de fornecer timestamps, muda seus termos ou passa a exigir credenciais.
- O piloto abre a camada enquanto o mapa de ruas, OpenAIP ou outra base está selecionada.
- REDEMET e RainViewer estão indisponíveis ao mesmo tempo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O mapa MUST oferecer RainViewer como camada suplementar de radar distinta da camada oficial REDEMET.
- **FR-002**: RainViewer MUST ser ativada somente por escolha explícita do piloto e MUST iniciar desligada.
- **FR-003**: A camada MUST ser identificada em português como RainViewer e como dado de radar não oficial; MUST exibir crédito visível com link para o provedor enquanto estiver ativa.
- **FR-004**: A camada MUST apresentar o horário do frame quando fornecido pela fonte e MUST NOT representar a hora de geração do manifesto como horário da observação.
- **FR-005**: Ausência de cobertura, frame, tile válido ou resposta do serviço MUST ser indicada como indisponibilidade, sem imagem inventada, substituição silenciosa ou apresentação de outra fonte como RainViewer. A interface MUST distinguir área fora da cobertura de área sem eco por meio da informação de cobertura fornecida pela fonte; se não conseguir fazê-lo, MUST informar que a cobertura é desconhecida e não apresentar o vazio como ausência de chuva.
- **FR-006**: RainViewer MUST NOT substituir automaticamente a REDEMET, alterar seu estado ou ser apresentada como radar oficial; a disponibilidade de cada fonte MUST permanecer distinguível.
- **FR-007**: A camada MUST NOT alterar a base cartográfica, rota, zoom, trechos, cálculo ou aceitabilidade do plano.
- **FR-008**: A camada MUST NOT ser usada para calcular vento, rota, combustível ou aceitabilidade, nem para autorizar decisões operacionais de voo.
- **FR-009**: O uso MUST permanecer compatível com os termos vigentes do provedor e com a finalidade educacional do produto. Se o uso permitido, a atribuição ou o acesso sem chave não puderem ser confirmados, a camada MUST ficar indisponível.

### Key Entities

- **Camada RainViewer**: Sobreposição suplementar, não oficial, ativada explicitamente e independente da REDEMET.
- **Frame de radar**: Imagem de precipitação com horário de frame e cobertura fornecidos pela fonte quando disponíveis.
- **Estado da fonte**: Disponibilidade e motivo de indisponibilidade apresentados separadamente para RainViewer e REDEMET.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os testes com RainViewer disponível, o piloto consegue ativar e desativar a camada sem trocar a base nem perder a rota.
- **SC-002**: Em 100% dos testes, a atribuição RainViewer aparece enquanto seus dados estão ativos e a identificação não sugere que a fonte seja oficial.
- **SC-003**: Em todos os testes de erro, falta de frame ou falta de cobertura, o mapa informa indisponibilidade sem exibir dados de outra fonte sob o rótulo RainViewer.
- **SC-004**: Em todos os testes, a indisponibilidade da REDEMET não bloqueia uma consulta RainViewer disponível, e uma falha RainViewer não altera o estado da REDEMET.
- **SC-005**: O uso da camada pública não exige uma chave configurada pelo piloto, desde que os termos vigentes do provedor continuem permitindo o uso educacional pretendido.

## Assumptions

- A finalidade do produto permanece exclusivamente didática e de desenvolvimento de software.
- A camada oficial REDEMET e sua indicação de disponibilidade permanecem inalteradas.
- RainViewer é uma opção suplementar, não uma substituição automática nem uma validação operacional do tempo.
- A API pública consultada durante a especificação não exigia chave e permitia uso educacional com atribuição, sem garantia de disponibilidade; essas condições precisam ser revalidadas antes da implementação.
- Cobertura e disponibilidade de radar variam por região e podem mudar sem aviso; cada resposta deve ser tratada segundo os dados fornecidos pela fonte.
