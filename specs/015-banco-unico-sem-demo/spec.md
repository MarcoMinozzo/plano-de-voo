# Feature Specification: Banco único e perfis sintéticos didáticos

**Feature Branch**: `main`

**Created**: 2026-11-25

**Status**: Draft

**Input**: Orientação do usuário: usar um único banco de produto, remover o modo DEMO e manter os vinte perfis sintéticos existentes para uso didático, sem validação aeronáutica.

## User Scenarios & Testing

### User Story 1 - Consolidar os perfis existentes (Priority: P1)

Como responsável pela aplicação, quero levar os vinte perfis sintéticos da antiga base DEMO para a base principal sem alterar a origem, para que o conteúdo didático continue disponível.

**Why this priority**: A consolidação não pode apagar os perfis que o usuário decidiu manter.

**Independent Test**: Executar a migração em duas bases isoladas e comparar a quantidade e os valores antes e depois.

**Acceptance Scenarios**:

1. **Given** a base principal com ROTAER e RAB e a antiga base com os vinte proxies, **When** a migração termina, **Then** os vinte proxies e seus valores sintéticos ficam disponíveis na base principal e a antiga base permanece intacta.
2. **Given** os mesmos perfis já migrados, **When** a migração é repetida, **Then** não cria duplicatas nem altera os registros.
3. **Given** perfil ausente ou conflito de valores, **When** a migração é executada, **Then** informa o problema e não altera as bases.

### User Story 2 - Usar aeronaves sintéticas para fins didáticos (Priority: P1)

Como piloto em treinamento, quero selecionar os vinte perfis em uma categoria distinta das aeronaves com dados factuais e entender que seus valores não foram validados.

**Why this priority**: O usuário quer manter esses perfis para estudo, sem apresentá-los como dados reais.

**Independent Test**: Consultar a seleção, criar um plano com um proxy e verificar o aviso na tela e no PDF.

**Acceptance Scenarios**:

1. **Given** os vinte perfis migrados, **When** a seleção é exibida, **Then** todos aparecem como perfis sintéticos didáticos e os perfis genéricos “Aeronave DEMO 01–20” não aparecem.
2. **Given** um perfil proxy selecionado, **When** um plano é calculado ou impresso, **Then** o resultado informa que os valores são sintéticos, não validados e não representam o modelo associado, além de manter o aviso de não uso real.

### User Story 3 - Operar sem modo DEMO (Priority: P1)

Como responsável pela aplicação, quero que a execução normal use uma única base de produto e que os testes continuem isolados, sem alternar entre bancos por modo.

**Why this priority**: A seleção de banco não deve depender de configuração DEMO e os testes não podem atingir os dados de produto.

**Independent Test**: Iniciar app e migrações com a configuração principal e confirmar que testes apontam para uma base distinta.

**Acceptance Scenarios**:

1. **Given** configurações antigas de DEMO presentes ou ausentes, **When** app e migrações iniciam, **Then** usam a mesma base principal.
2. **Given** a configuração da base principal ausente ou inválida, **When** a aplicação inicia, **Then** falha explicitamente sem abrir uma sessão de banco.

### Edge Cases

- A origem da migração não contém exatamente os vinte proxies: informar quais faltam e não alterar o destino.
- O destino já contém perfil com mesmo identificador e valores idênticos: tratar como já migrado; se os dados diferirem, abortar sem sobrescrever.
- A base principal não tem extrato RAB disponível: os vinte proxies continuam visíveis na categoria didática; o catálogo factual continua indisponível e o cálculo de rota continua sujeito ao ROTAER oficial.
- ROTAER indisponível: manter a indisponibilidade explícita para o cálculo de rota, sem substituir a fonte oficial por dados sintéticos.

## Requirements

### Functional Requirements

- **FR-001**: A aplicação MUST usar uma única base de dados de produto, sem modo DEMO ou seleção de uma segunda base durante a execução normal.
- **FR-002**: O ambiente de testes MUST continuar usando uma base separada da base de produto.
- **FR-003**: A migração MUST copiar exatamente os vinte proxies existentes e preservar seus seis valores técnicos e unidades sem validá-los, recalculá-los ou alterá-los.
- **FR-004**: A migração MUST preservar ROTAER e RAB já existentes no destino e MUST NOT copiar pilotos, planos, perfis genéricos ou o extrato RAB sintético da antiga base.
- **FR-005**: A migração MUST ser repetível sem duplicar registros. Diante de origem incompleta ou conflito divergente, MUST informar o problema e não sobrescrever nem modificar dados.
- **FR-006**: Os vinte proxies MUST permanecer disponíveis numa categoria didática separada, sem contar entre os trinta modelos factuais nem depender da validação de suas fontes aeronáuticas.
- **FR-007**: Seleção, plano, resultado e PDF MUST identificar os valores dos proxies como sintéticos, não validados e sem correspondência comprovada com o modelo associado; MUST preservar o aviso de que o sistema não serve para voo real e não autoriza voo.
- **FR-008**: Os vinte perfis genéricos “Aeronave DEMO 01–20” MUST NOT ser migrados nem oferecidos.
- **FR-009**: A antiga base DEMO MUST permanecer intacta após a migração.

### Key Entities

- **Perfil proxy sintético**: perfil didático associado a um modelo como alvo de exercício, com valores e unidades sintéticos, não validados.
- **Catálogo factual de aeronaves**: modelos sujeitos às regras normais de fonte, completude e limite do produto; proxies não contam nesse catálogo.
- **Base de origem**: banco antigo usado apenas para leitura durante a migração; não transfere pilotos nem planos.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Os 20 perfis proxy existentes ficam disponíveis após a transição, com 100% dos valores técnicos e unidades preservados.
- **SC-002**: A migração pode ser repetida sem aumentar a quantidade de perfis nem alterar valores já importados.
- **SC-003**: Nenhum perfil genérico, piloto ou plano da antiga base DEMO é copiado; a base de origem não sofre alterações.
- **SC-004**: Em todos os pontos de seleção, resultado e PDF, cada proxy é identificado como sintético e não validado.
- **SC-005**: Os testes usam uma base distinta da base de produto.

## Assumptions

- A base atual de produto é a fonte canônica e já contém ROTAER e RAB.
- A antiga base DEMO estará acessível como origem somente de leitura durante a migração.
- Os vinte proxies existentes permanecem como estão; não haverá pesquisa nem validação aeronáutica nesta mudança.
- Pilotos e planos da antiga base DEMO não precisam ser preservados na base nova, conforme decisão do usuário.
