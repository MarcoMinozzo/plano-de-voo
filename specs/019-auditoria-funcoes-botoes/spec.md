# Feature Specification: Auditoria de funções, botões e camadas

**Feature Branch**: `019-auditoria-funcoes-botoes`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Revise todas as funções e botões do aplicativo; várias ações não funcionam, como salvar o nome de exibição e controlar as camadas do mapa."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Salvar o nome de exibição (Priority: P1)

Como piloto, quero salvar meu nome de exibição e saber que a alteração foi concluída, para confiar no resultado sem confundi-lo com minha identificação de acesso.

**Why this priority**: O usuário relatou diretamente que o salvamento parece não funcionar.

**Independent Test**: Em ambiente isolado, salvar um nome válido e verificar persistência, confirmação e isolamento do perfil.

**Acceptance Scenarios**:

1. **Given** um perfil autenticado e um nome válido, **When** o piloto salva, **Then** o nome fica gravado e a tela confirma o sucesso.
2. **Given** uma entrada inválida, **When** o piloto tenta salvar, **Then** a validação é mostrada e não aparece confirmação de sucesso.

---

### User Story 2 - Consultar as camadas do mapa (Priority: P1)

Como piloto, quero entender quais camadas do mapa estão disponíveis e por quê, para usar a base e a rota sem confundir uma camada indisponível com uma falha silenciosa.

**Why this priority**: O usuário relatou diretamente problemas nas camadas do mapa.

**Independent Test**: Com rota válida, alternar trechos e verificar base, rota e estado de cada camada em cenários disponível e indisponível.

**Acceptance Scenarios**:

1. **Given** uma rota e a base de ruas disponível, **When** o piloto alterna os trechos, **Then** a rota permanece visível e somente uma aba fica selecionada.
2. **Given** WAC, OpenAIP ou radar sem validação, cobertura ou configuração necessária, **When** o piloto consulta os controles, **Then** a camada permanece indisponível e o motivo conhecido é informado sem substituição enganosa.

---

### User Story 3 - Usar controles em telas estreitas (Priority: P2)

Como piloto em um telefone, quero consultar os mesmos dados e controles sem a página se expandir além da tela, para alcançar o conteúdo sem rolagem horizontal do documento inteiro.

**Why this priority**: A tabela larga atualmente faz o conteúdo exceder a viewport móvel.

**Independent Test**: Abrir o plano em viewports de 390 px e 1440 px e verificar dimensões, rolagem interna da tabela e acesso aos controles.

**Acceptance Scenarios**:

1. **Given** o plano em viewport de 390 px, **When** a tabela de fontes é exibida, **Then** a rolagem horizontal fica contida na tabela e a página não excede a viewport.
2. **Given** qualquer viewport testada, **When** o piloto usa navegação, formulário ou controle disponível, **Then** a ação conclui ou apresenta seu estado indisponível claramente.

### Edge Cases

- Salvamento inválido não pode gerar mensagem de sucesso.
- Tiles cancelados durante reposicionamento do mapa não devem ser tratados como falha persistente quando os tiles atuais carregam.
- Camada sem chave, cobertura ou validação permanece indisponível; não há fallback que represente uma fonte como outra.
- A tabela mantém todas as colunas, mesmo quando precisa de rolagem horizontal interna.
- A auditoria não envia formulários de produção nem executa ações destrutivas para testar controles.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O perfil MUST confirmar visualmente um salvamento somente depois que o nome válido tiver sido persistido.
- **FR-002**: O perfil MUST preservar a validação existente, o valor recusado no formulário e o isolamento entre pilotos.
- **FR-003**: O mapa MUST manter a rota e a aba selecionada ao alternar entre trechos ou camadas disponíveis.
- **FR-004**: O mapa MUST informar o motivo conhecido para cada camada indisponível e MUST NOT substituir silenciosamente WAC, OpenAIP ou radar por outra fonte.
- **FR-005**: WAC MUST permanecer indisponível até que edição vigente, georreferenciamento, cobertura e autorização tenham sido validados; OpenAIP e radar MUST respeitar seus requisitos de chave, licença e limites geográficos.
- **FR-006**: Em viewport de 390 px, a tabela larga MUST rolar dentro de sua própria área sem expandir a página nem ocultar colunas; em 1440 px a apresentação permanece legível.
- **FR-007**: Os controles visíveis MUST ser verificados por testes existentes ou navegação não destrutiva e classificados como funcionando, indisponíveis com motivo, ou falhando.
- **FR-008**: A auditoria MUST preservar dados, cálculos, sessão e avisos existentes; testes que poderiam alterar dados reais MUST usar ambiente isolado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os testes de salvamento válido, o nome permanece gravado e a confirmação só aparece depois da conclusão; entradas inválidas nunca exibem sucesso.
- **SC-002**: Em 100% dos cenários testados de camada indisponível, a tela informa o motivo conhecido e não mostra substituição enganosa.
- **SC-003**: Em viewports de 390 px e 1440 px, a largura do documento não excede a viewport; todas as colunas continuam acessíveis.
- **SC-004**: Cada controle primário auditado termina classificado como funcionando, bloqueado por requisito identificado ou falhando com caso reproduzível.

## Assumptions

- O nome de exibição é independente da identificação de acesso e a gravação já está implementada.
- Tiles de ruas podem ser cancelados quando o mapa reposiciona; isso não basta para concluir que a base falhou se as imagens atuais carregarem.
- WAC, OpenAIP e radar não serão ativados sem seus gates de validação, configuração, licença e georreferenciamento.
- O resumo da auditoria apresentará os controles verificados e os bloqueios externos, sem acrescentar avisos didáticos redundantes.
