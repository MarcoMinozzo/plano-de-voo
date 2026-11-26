# Especificação de Funcionalidade: Integrar Tailwind CSS

**Feature Branch**: `008-integrar-tailwind`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "VAMOPS INCLUIR O TAILWIND NO PROJETO PARA FACILITAR A ESTILIZACAO"

## User Scenarios & Testing

### User Story 1 - Estilizar as telas com Tailwind (Priority: P1)

Como equipe que mantém o Plano de voo, queremos aplicar e ajustar estilos com utilitários Tailwind nas páginas existentes, sem reconstruir o visual aprovado, para facilitar a evolução da interface.

**Why this priority**: A adoção será útil quando as telas atuais puderem receber os utilitários sem perder a identidade e os comportamentos responsivos.

**Independent Test**: Compilar e abrir as telas de entrada, cadastro, painel e plano em larguras móveis e desktop, comparando a casca e exercitando os controles existentes.

**Acceptance Scenarios**:

1. **Given** a folha de estilos do projeto compilada, **When** qualquer página existente é aberta, **Then** ela carrega a folha e conserva a casca visual aprovada.
2. **Given** uma classe utilitária usada em um template, **When** a folha é compilada, **Then** a classe está disponível no CSS entregue à página.
3. **Given** uma janela estreita ou desktop, **When** a tela é exibida, **Then** o conteúdo mantém o comportamento responsivo atual, incluindo a ausência de rolagem horizontal indevida.

### User Story 2 - Preservar os fluxos do piloto (Priority: P1)

O piloto continua usando entrada, cadastro, planejamento, lista, abas, impressão e saída como antes da adoção do novo estilo.

**Why this priority**: A mudança de estilo não pode interromper os fluxos já usados para planejar e consultar um voo.

**Independent Test**: Executar os testes existentes da casca visual e dos fluxos do piloto após a migração.

**Acceptance Scenarios**:

1. **Given** o formulário de plano, **When** o piloto o envia, **Then** o estado "Em processamento" e o bloqueio de navegação continuam funcionando.
2. **Given** a navegação autenticada, **When** o piloto usa menu, abas ou impressão, **Then** cada ação mantém o comportamento existente.

### Edge Cases

- Se as classes de um template não forem detectadas, a validação do build deve identificar CSS ausente antes de considerar a integração concluída.
- Se a compilação não tiver sido executada, o serviço deve falhar de forma explícita no build/operação, não ocultar o problema com uma folha remota.
- Uma classe condicional de Jinja deve continuar incluída no CSS gerado.
- Uma tela renderizada sem autenticação continua sem apresentar o menu autenticado.

## Requirements

### Functional Requirements

- **FR-001**: As páginas existentes MUST usar a folha de estilos Tailwind produzida pelo projeto.
- **FR-002**: O projeto MUST permitir que a equipe aplique utilitários Tailwind nos templates e inclua as classes utilizadas na folha entregue.
- **FR-003**: A identidade visual aprovada MUST permanecer equivalente, incluindo cores, card, menu, ampulheta, tipografia e pontos de quebra.
- **FR-004**: A adoção MUST NOT alterar cálculo, dados, endpoints, conteúdo do plano, permissões nem fluxos de navegação.
- **FR-005**: Os fluxos existentes de entrada, cadastro, processamento, resumo, abas, impressão e saída MUST continuar operacionais.
- **FR-006**: A folha usada pelo Flask MUST estar disponível como asset local, sem depender de CDN ou watcher ativo durante requisições.
- **FR-007**: A equipe MUST ter instruções claras para instalar as ferramentas de estilo, compilar a folha e mantê-la em modo de observação durante desenvolvimento.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Todas as páginas cobertas pelo teste da casca carregam a folha local compilada.
- **SC-002**: 100% dos testes existentes de casca e fluxos do piloto continuam aprovados após a migração.
- **SC-003**: Em larguras estreitas e desktop, as páginas mantêm a casca visual atual sem overflow horizontal introduzido.
- **SC-004**: Uma classe utilitária usada em template aparece na folha gerada após o build.
- **SC-005**: O app local serve CSS sem precisar manter um processo de compilação em execução durante as requisições.

## Assumptions

- Tailwind CSS é a ferramenta solicitada para facilitar as próximas alterações de estilo.
- A adoção inclui migrar o CSS atual da casca para utilitários Tailwind, mas não redesenhar as telas.
- Dependências e artefatos de estilo devem ser locais e reproduzíveis; a aplicação continua servida pelo Flask.
- A folha compilada pode ser gerada antes de iniciar o serviço e mantida no repositório para que o runtime não dependa de Node.
