# Feature Specification: Catálogo sintético isolado para DEMO

**Feature Branch**: `006-catalogo-demo-sintetico`

**Created**: 2026-11-24

**Status**: Draft

**Input**: Pedido do usuário para inserir imediatamente dados de aeronaves, com autorização para um catálogo sintético somente em DEMO, isolado e bloqueado em produção.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Abrir o catálogo DEMO (Priority: P1)

Como pessoa desenvolvedora, quero consultar vinte perfis sintéticos de aeronaves para continuar o desenvolvimento sem esperar pela pesquisa de vinte modelos reais completos.

**Why this priority**: O catálogo didático real continua condicionado a fontes rastreáveis e à validação do RAB. Perfis sintéticos permitem exercitar seleção e cálculos sem atribuir números inventados a modelos reais.

**Independent Test**: Em ambiente DEMO isolado, carregar o catálogo e confirmar vinte perfis com valores e rótulos sintéticos; no ambiente normal, confirmar que nenhum desses perfis é oferecido.

**Acceptance Scenarios**:

1. **Given** a aplicação está no ambiente DEMO autorizado, **When** a pessoa desenvolvedora consulta aeronaves, **Then** vê vinte perfis com nomes demonstrativos, unidades e rótulo explícito de dados sintéticos.
2. **Given** o catálogo sintético foi carregado, **When** a pessoa desenvolvedora consulta os dados técnicos, **Then** velocidade e consumo usam o mesmo perfil fictício e todos os campos obrigatórios têm valores didáticos claramente identificados.
3. **Given** há uma emenda oficial vigente do ROTAER carregada no armazenamento DEMO, **When** a pessoa desenvolvedora cria um plano usando um perfil sintético, **Then** a rota usa somente os aeródromos publicados nessa emenda e mantém o aviso não operacional.

---

### User Story 2 - Impedir mistura com dados de produção (Priority: P1)

Como responsável pela operação, quero que dados sintéticos não sejam acessíveis nem gravados pelo catálogo de produção.

**Why this priority**: A separação evita que valores inventados sejam confundidos com informações rastreáveis de aeronaves reais.

**Independent Test**: Iniciar a aplicação em produção com uma configuração DEMO ou uma origem de dados ausente/compartilhada e confirmar falha explícita, sem consultar nem alterar o banco de produção.

**Acceptance Scenarios**:

1. **Given** o ambiente é produção, **When** a configuração DEMO é solicitada, **Then** a aplicação recusa a inicialização.
2. **Given** o ambiente é DEMO, **When** não há armazenamento DEMO exclusivo configurado, **Then** a aplicação recusa a inicialização sem recorrer ao armazenamento normal.
3. **Given** registros sintéticos existem no armazenamento, **When** a aplicação inicia no modo normal, **Then** nenhum perfil sintético aparece na seleção nem é aceito para cálculo.

## Edge Cases

- A configuração DEMO aponta para a mesma origem de dados usada pelo ambiente normal.
- O armazenamento DEMO contém dados de uma execução anterior; repetir a carga não duplica registros.
- Um perfil sintético está incompleto ou usa unidades incompatíveis; ele não fica disponível para cálculo.
- O perfil sintético é apresentado em tela, resultado ou PDF; cada apresentação preserva o rótulo de demonstração e o aviso não operacional.
- Não há emenda oficial vigente do ROTAER no armazenamento DEMO; o catálogo de aeródromos permanece indisponível e nenhum plano é criado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A aplicação MUST oferecer um modo DEMO explícito, disponível somente fora do ambiente de produção.
- **FR-002**: O modo DEMO MUST usar armazenamento exclusivo, diferente do armazenamento normal; configuração ausente, inválida ou compartilhada MUST causar erro explícito, sem fallback.
- **FR-003**: O catálogo DEMO MUST conter vinte perfis com nomes demonstrativos, sem atribuir valores sintéticos a modelos reais.
- **FR-004**: Cada perfil MUST conter os campos técnicos usados nos cálculos, unidades explícitas e velocidade e consumo vinculados ao mesmo perfil sintético.
- **FR-005**: Cada valor sintético MUST ser identificado em tela, resultado e PDF como dado de DEMO que não corresponde a uma aeronave real, não serve para planejamento de voo real e não autoriza o voo.
- **FR-006**: O modo normal MUST excluir perfis sintéticos da seleção e MUST recusá-los em cálculos, mesmo que registros sintéticos estejam presentes no armazenamento normal.
- **FR-007**: A carga DEMO MUST ser reproduzível e idempotente, sem apagar ou modificar dados existentes fora do armazenamento DEMO.
- **FR-008**: Planos no modo DEMO MUST exigir uma emenda oficial vigente do ROTAER no armazenamento DEMO; o sistema MUST NOT inventar aeródromos, coordenadas, vento, meteorologia, carta ou pôr do sol para completar um plano.

### Key Entities *(include if feature involves data)*

- **Perfil sintético de aeronave**: conjunto fictício de valores e unidades para exercitar seleção e cálculos; não representa marca, modelo ou aeronave real.
- **Ambiente DEMO**: contexto isolado que pode ler e gravar apenas os dados sintéticos destinados ao desenvolvimento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A consulta DEMO retorna exatamente vinte perfis identificados como sintéticos.
- **SC-002**: A inicialização normal nunca oferece nem aceita perfis sintéticos, inclusive quando a configuração de DEMO está presente.
- **SC-003**: Configuração de DEMO sem armazenamento exclusivo ou em produção resulta em erro explícito antes de qualquer escrita.
- **SC-004**: Repetir a carga DEMO mantém vinte perfis, sem duplicação e sem alterar o armazenamento normal.
- **SC-005**: Sem emenda ROTAER oficial vigente no armazenamento DEMO, nenhum plano de rota é criado; com a emenda disponível, a rota usa somente seus aeródromos.

## Assumptions

- Os nomes serão genéricos, como “Aeronave DEMO 01”, para não atribuir dados inventados a modelos reais.
- Os dados servirão apenas a desenvolvimento e verificação do software; o modo DEMO não afirma a validade de rotas ou condições operacionais.
- O ROTAER oficial vigente pode ser carregado separadamente no armazenamento DEMO; nenhum dado de navegação ou condição de voo será sintético.
- O catálogo técnico real permanece sujeito à especificação ativa de fontes rastreáveis e não será substituído por estes perfis.
