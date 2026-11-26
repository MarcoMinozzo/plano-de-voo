# Feature Specification: Proxies de aeronaves em DEMO

**Feature Branch**: `007-proxies-aeronaves-demo`

**Created**: 2026-11-24

**Status**: Draft

**Input**: Spec aprovada em `_bmad-output/implementation-artifacts/spec-planos-demo-com-proxies-sinteticos.md` e ordem do usuário para integrar e fazer funcionar.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Planejar usando proxy de modelo (Priority: P1)

Como pessoa desenvolvedora, quero selecionar um perfil de teste associado a um modelo elegível e gerar um plano DEMO, para exercitar cálculos e apresentação sem tratar valores sintéticos como dados reais.

**Why this priority**: O fluxo de ponta a ponta é o resultado principal solicitado; os dados de aeronave podem ser proxies, mas aeródromos e condições de voo continuam oficiais.

**Independent Test**: Com ROTAER vigente em fixture e respostas oficiais simuladas, selecionar um proxy e criar um plano DEMO; confirmar que o plano preserva a procedência do proxy e não inventa dados de navegação ou meteorologia.

**Acceptance Scenarios**:

1. **Given** o DEMO contém perfis genéricos e proxies elegíveis, **When** a pessoa desenvolvedora consulta o catálogo, **Then** os dois grupos permanecem disponíveis na API e claramente diferenciados.
2. **Given** a pessoa desenvolvedora abre o formulário de novo plano, **When** escolhe uma aeronave, **Then** cada opção mostra somente o nome cadastrado, sem avisos ou fontes técnicas anexados; os avisos DEMO ficam fora da lista e a procedência detalhada permanece no resultado e no PDF.
3. **Given** o catálogo DEMO mantém perfis genéricos e proxies, **When** a pessoa abre a seleção de aeronave, **Then** os perfis genéricos não são oferecidos e os proxies aparecem pelo nome do modelo-alvo, sem o prefixo “Proxy DEMO”.
4. **Given** um proxy completo e uma emenda ROTAER oficial vigente, **When** um plano é solicitado com respostas meteorológicas simuladas, **Then** o servidor calcula o plano usando os aeródromos da emenda e mantém o aviso DEMO não operacional.
5. **Given** ausência de emenda vigente ou falha/cobertura ausente de uma fonte oficial, **When** o plano é solicitado, **Then** o sistema recusa a rota sem ROTAER ou informa o item meteorológico como indisponível, sem substituí-lo por valor sintético.

### User Story 2 - Conferir a origem e os limites dos valores (Priority: P1)

Como pessoa desenvolvedora, quero conferir, para cada campo sintético selecionável, inclusive nos perfis genéricos existentes, a faixa de geração, as fontes que a justificam e o método usado, para reproduzir testes sem confundir a faixa com um limite operacional.

**Why this priority**: Um proxy sem faixa justificável e rastreável não permite testar o comportamento com segurança nem satisfaz a constituição.

**Independent Test**: Consultar todos os campos genéricos e de proxy e confirmar unidade, valor dentro da faixa, evidência, aplicabilidade, método, versão/semente e incerteza; tentar cadastrar valor fora da faixa e confirmar recusa.

**Acceptance Scenarios**:

1. **Given** um campo sintético elegível, genérico ou de proxy, **When** sua procedência é consultada, **Then** são apresentados o valor, unidade, limites inferior e superior, referências e aplicabilidade, método, versão/semente e incerteza.
2. **Given** um campo sem evidência suficiente ou valor fora da faixa, **When** o catálogo é validado, **Then** o campo não torna o proxy elegível e o sistema informa a lacuna.
3. **Given** peso, bagagem, combustível, velocidade e consumo de um proxy, **When** a elegibilidade é validada, **Then** as relações físicas são coerentes e velocidade e consumo pertencem ao mesmo perfil nominal.

### User Story 3 - Manter o isolamento DEMO e repetir a carga (Priority: P1)

Como responsável pelo desenvolvimento, quero repetir a carga dos proxies sem duplicar registros, perder os perfis genéricos ou alterar planos existentes, e sem expor sintéticos no catálogo normal.

**Why this priority**: A aplicação precisa continuar testável em DEMO sem misturar dados de teste com o catálogo normal ou destruir histórico.

**Independent Test**: Carregar os proxies duas vezes em banco DEMO isolado; confirmar os 20 perfis genéricos e até 20 proxies selecionáveis, planos históricos intactos e nenhum proxy elegível no modo normal.

**Acceptance Scenarios**:

1. **Given** banco DEMO com perfis genéricos e planos, **When** a carga de proxies é repetida, **Then** a carga não duplica proxies nem altera os perfis ou planos existentes.
2. **Given** o DEMO contém 20 genéricos e até 20 proxies elegíveis, **When** o catálogo é consultado, **Then** todos podem ser selecionados; o modo normal mantém o limite de 30 e exclui todos os sintéticos.
3. **Given** configuração DEMO ausente, compartilhada ou solicitada fora de `development`, **When** a aplicação inicia, **Then** falha explicitamente antes de conectar ou usar o banco normal.

### Edge Cases

- Um candidato do ranking RAB excede 5.670 kg ou sua classe/peso máximo aprovado não pode ser verificado: não criar proxy elegível; continuar a triagem.
- Não há referência suficiente para delimitar a faixa de um campo: deixá-lo indisponível e não usar valor substituto.
- Há conflito entre referências: preservar a divergência e a incerteza; não calcular média.
- O ROTAER não tem emenda vigente no DEMO: nenhuma rota é criada.
- A fonte oficial de meteorologia, vento, carta ou radar falha ou não cobre a rota: apresentar indisponibilidade, sem síntese ou fallback.
- Uma carga já executada é repetida ou existem planos antigos ligados aos perfis genéricos: preservar os registros e o histórico.
- Um perfil sintético aparece no modo normal ou chega por envio direto: ocultar ou recusar no servidor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Perfis proxy MUST existir somente em modo DEMO explicitamente habilitado em ambiente de desenvolvimento, com armazenamento dedicado e sem fallback para o armazenamento normal.
- **FR-002**: O catálogo DEMO MUST manter os 20 perfis genéricos existentes e oferecer até 20 proxies elegíveis associados como alvos de teste a modelos reais. O formulário de novo plano MUST NOT oferecer os perfis genéricos e MUST exibir os proxies somente pelo nome do modelo-alvo.
- **FR-003**: A triagem MUST partir do ranking preliminar do RAB, validar avião pequeno e peso máximo aprovado de até 5.670 kg, e continuar no ranking até encontrar 20 modelos elegíveis. O ranking, por si só, não prova classe nem peso.
- **FR-004**: Um proxy MUST permanecer inelegível quando faltar evidência suficiente para qualquer campo técnico obrigatório usado no cálculo.
- **FR-005**: Para peso vazio, peso máximo de decolagem, limite de bagagem, combustível utilizável, velocidade de cruzeiro e consumo de cruzeiro, cada perfil sintético selecionável, genérico ou proxy, MUST guardar unidade, valor, limites inferior/superior, referências que justificam a faixa, aplicabilidade, método de geração, versão/semente reprodutível e incerteza.
- **FR-006**: Cada faixa MUST ser fundamentada em referência rastreável aplicável ao modelo/variante exato ou, na ausência dela, em pelo menos duas referências técnicas rastreáveis de modelos comparáveis, com justificativa de comparabilidade.
- **FR-007**: Valores gerados MUST ficar dentro das faixas e respeitar relações físicas, incluindo peso máximo de decolagem acima do peso vazio, bagagem dentro da carga útil disponível e velocidade/consumo do mesmo perfil nominal.
- **FR-008**: A data editorial dos campos sintéticos MUST ser apresentada como “não se aplica”; a data de consulta MUST permanecer separada e não pode substituí-la.
- **FR-009**: Seleção, plano, resultado e PDF MUST identificar “DEMO — proxy sintético”, a associação como alvo de teste, que os valores não são fatos nem dados aprovados para o modelo, e que o resultado não serve para voo real nem o autoriza.
- **FR-010**: Planos DEMO MUST exigir ROTAER oficial vigente no banco DEMO. Aeródromos, coordenadas, METAR/TAF, vento, cartas, radar e pôr do sol MUST vir exclusivamente de fontes oficiais; falha ou falta de cobertura MUST ser mostrada como indisponibilidade.
- **FR-011**: O modo normal MUST excluir proxies da seleção e recusá-los em cálculos, inclusive por envio direto; seu limite de catálogo permanece 30.
- **FR-012**: A carga MUST ser idempotente, preservar perfis genéricos e planos existentes, e não alterar dados da base normal.
- **FR-013**: O formulário de novo plano MUST NOT exibir menus expansíveis de fontes técnicas para cada aeronave. Cada opção MUST mostrar somente o nome cadastrado, sem metadados anexados; os avisos DEMO ficam fora da lista e a procedência detalhada permanece no resultado e no PDF.
- **FR-014**: Na seleção de aeronaves DEMO, o sistema MUST exibir um aviso geral identificando os valores como “DEMO — proxy sintético” e alvos de teste; MUST NOT anexar “Proxy DEMO” ao nome do modelo em cada opção.

### Key Entities *(include if feature involves data)*

- **Proxy sintético**: perfil DEMO associado a um modelo apenas como alvo de teste, com campos técnicos, faixas, referências, método, versão/semente e incerteza.
- **Evidência de faixa**: referência técnica, publicador, data disponível, modelo/variante e justificativa de aplicabilidade/comparabilidade.
- **Perfil genérico DEMO**: perfil sintético existente, preservado e selecionável junto dos proxies.
- **Plano DEMO**: plano que usa perfil DEMO e dados oficiais de aeródromo e meteorologia, com procedência e aviso não operacional.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O catálogo DEMO mantém os 20 perfis genéricos e até 20 proxies elegíveis, mas o formulário de plano oferece somente os proxies, identificados pelo nome do modelo-alvo.
- **SC-002**: 100% dos campos sintéticos selecionáveis, genéricos ou proxy, têm valor, unidade, faixa, evidências, aplicabilidade, método, versão/semente e incerteza; nenhum valor selecionado fica fora de sua faixa.
- **SC-003**: Uma carga DEMO repetida não duplica proxies nem altera perfis genéricos, planos históricos ou dados da base normal.
- **SC-004**: Um plano de teste com proxy, ROTAER fixture vigente e fontes oficiais simuladas conclui o fluxo; cada opção da seleção exibe somente o nome cadastrado, sem menus de fontes técnicas, e o resultado/PDF mantêm os avisos e a procedência detalhada.
- **SC-005**: Sem ROTAER vigente, fonte oficial com falha ou modo DEMO válido, o sistema recusa o uso aplicável ou exibe indisponibilidade sem inventar dados.
- **SC-006**: O catálogo normal não lista nem calcula qualquer proxy, e continua limitado a 30 modelos.

## Assumptions

- Os proxies são exclusivamente para desenvolvimento de software. Não são dados factuais, certificados, envelopes de voo ou limites do fabricante.
- O ranking RAB é apenas uma ordem de pesquisa; classe, peso máximo e evidência técnica devem ser verificados individualmente.
- AOPA, Pilot-Next, Aeroway e FAA são pontos de partida, não validação automática. Só referências técnicas aplicáveis justificam campos e faixas.
- Se não houver evidência suficiente para um candidato ou campo, a lacuna permanece indisponível; não se inventa valor para completar a lista.
- A emenda oficial ROTAER AMDT 47/26 já está carregada na base normal do projeto, com 4.519 aeródromos. A preparação do DEMO deve copiar essa publicação oficial para a base isolada; não precisa baixar a lista pela API do AISWEB.
- Credenciais AISWEB/REDEMET podem ser necessárias para carta, pôr do sol e vento em consultas reais; sua ausência mantém esses itens indisponíveis e não impede testes com respostas simuladas.
