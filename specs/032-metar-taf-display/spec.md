# Feature Specification: Apresentação legível de METAR e TAF

**Feature Branch**: `032-metar-taf-display`

**Created**: 2026-11-27

**Status**: Draft

**Input**: User description: "melhore a forma de apresentar na tela o metar e o TAF, mantenha o string original e coloque dentro de um campo preto com letras em branco (cinza 5%) como se posse ou imitasse uma tela de terminal , mas inclua tambem a leitura dos dados de foma tabular e organizada. Para os fenomenos meteorologicos crie um tradutor interno e imprima na tela a explicacao."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ler METAR e TAF em formato organizado (Priority: P1)

Como piloto, quero manter o boletim original e também consultar sua leitura em tabelas claras, para entender rapidamente as condições reportadas sem perder acesso à mensagem publicada.

**Why this priority**: O código original é essencial para conferir a interpretação, mas sua leitura isolada é difícil; a tabela deve facilitar a consulta sem substituir a fonte.

**Independent Test**: Exibir um plano com METAR e TAF conhecidos e conferir que cada mensagem original permanece integral e que os campos interpretáveis aparecem em tabelas organizadas.

**Acceptance Scenarios**:

1. **Given** um aeródromo com METAR e TAF disponíveis, **When** o usuário abre a ficha do trecho, **Then** cada string original aparece preservada em um bloco escuro monoespaçado com texto claro e os dados interpretados aparecem em tabelas em português.
2. **Given** um TAF com períodos de mudança, **When** o usuário consulta sua leitura tabular, **Then** validade, vento, visibilidade, fenômenos e nuvens ficam associados ao período a que se aplicam.
3. **Given** um boletim indisponível ou com campos que não podem ser interpretados, **When** a ficha é exibida, **Then** a indisponibilidade ou lacuna é indicada sem inventar valores, mantendo o boletim original quando existente.
4. **Given** uma tela estreita, **When** o usuário consulta as tabelas, **Then** os dados continuam legíveis sem exigir rolagem horizontal da página inteira.

### User Story 2 - Entender os códigos de fenômenos meteorológicos (Priority: P2)

Como piloto, quero ver uma explicação em português para os códigos de fenômenos que aparecem no METAR e no TAF, para entender o significado sem depender de uma consulta externa.

**Why this priority**: A explicação torna a leitura tabular acessível, preservando o código aeronáutico original para conferência.

**Independent Test**: Exibir códigos meteorológicos conhecidos e desconhecidos; confirmar que os conhecidos recebem explicações corretas em português e os desconhecidos permanecem identificados sem interpretação inventada.

**Acceptance Scenarios**:

1. **Given** um METAR ou TAF contém fenômenos conhecidos, **When** a tabela é exibida, **Then** cada fenômeno reconhecido aparece junto de sua explicação em português.
2. **Given** um boletim contém um código de fenômeno não reconhecido, **When** a tabela é exibida, **Then** o código original permanece visível e é marcado como não interpretado, sem atribuir significado não confirmado.
3. **Given** vários códigos de fenômeno aparecem combinados, **When** o usuário consulta a explicação, **Then** intensidade, descritor e fenômeno são apresentados sem duplicar nem ocultar o código original.

### Edge Cases

- Boletim válido contém grupos ou campos opcionais ausentes: omitir valores não fornecidos e identificar somente campos indisponíveis que a interface já apresenta.
- String original contém espaços ou grupos de mudança TAF: preservá-la integralmente no bloco original, ainda que a leitura tabular normalize espaçamento.
- Código de fenômeno está combinado, é desconhecido ou contém intensidade/descritor: explicar apenas componentes reconhecidos e manter o token original.
- METAR/TAF é indisponível: manter a mensagem de indisponibilidade já existente, sem produzir uma tabela com dados inferidos.
- Tela pequena: permitir rolagem dentro da tabela quando necessário, sem alargar o documento inteiro.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A tela MUST preservar e exibir a string original integral de cada METAR e TAF disponível, sem alterar o texto armazenado ou publicado.
- **FR-002**: O METAR original MUST aparecer em bloco escuro de aparência terminal, com fonte monoespaçada e texto claro de alto contraste.
- **FR-003**: O TAF original MUST aparecer em bloco escuro de aparência terminal, com fonte monoespaçada e texto claro de alto contraste.
- **FR-004**: A tela MUST apresentar uma leitura tabular em português para os campos METAR e TAF que puderem ser interpretados, sem substituir a mensagem original.
- **FR-005**: A leitura do TAF MUST associar grupos de previsão e mudança aos períodos de validade publicados, distinguindo períodos de base, FM, BECMG, TEMPO e PROB quando presentes.
- **FR-006**: Fenômenos meteorológicos reconhecidos MUST exibir uma explicação em português na tabela; o código publicado MUST continuar visível junto à explicação.
- **FR-007**: Códigos desconhecidos ou parcialmente reconhecidos MUST permanecer visíveis e ser identificados como não interpretados, sem explicação inventada.
- **FR-008**: A interface MUST manter fonte, horários e estados de disponibilidade já apresentados, sem alterar a independência entre METAR e TAF.
- **FR-009**: Tabelas MUST permanecer legíveis em telas estreitas, sem rolagem horizontal da página inteira.
- **FR-010**: A leitura e tradução MUST ser determinísticas e não depender de serviço externo durante a exibição.
- **FR-011**: Valores ausentes ou não interpretáveis MUST ser apresentados como indisponíveis ou não interpretados, sem inferência.
- **FR-012**: Textos, cabeçalhos, unidades e explicações MUST permanecer em português, preservando o aviso educacional do relatório.

### Key Entities

- **Boletim meteorológico**: String original METAR ou TAF, fonte, horário, aeródromo associado e estado de disponibilidade.
- **Campo interpretado**: Valor extraído do boletim, seu rótulo em português, unidade e período de validade aplicável.
- **Fenômeno meteorológico**: Código publicado e sua explicação em português quando houver interpretação interna conhecida.
- **Grupo de previsão TAF**: Condições base ou mudança previstas, relacionadas ao intervalo temporal publicado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os cenários de teste com METAR/TAF disponível, o texto original é idêntico ao texto fornecido pela fonte e continua visível.
- **SC-002**: Cada campo de METAR/TAF explicitamente coberto pelos casos de teste aparece em tabela com rótulo e unidade aplicáveis.
- **SC-003**: Todos os códigos de fenômenos cobertos pelo catálogo interno de teste exibem explicação em português; códigos desconhecidos aparecem sem significado inventado.
- **SC-004**: Casos TAF com grupos base, FM, BECMG, TEMPO e PROB mantêm os campos vinculados ao período correto.
- **SC-005**: Na largura móvel de 390 px, o conteúdo pode ser consultado sem rolagem horizontal do documento.

## Assumptions

- A apresentação é alterada na página de detalhes do plano; a geração de novas fontes meteorológicas e os cálculos de rota permanecem inalterados.
- A interpretação é didática e não substitui a mensagem oficial, a formação meteorológica ou a validação operacional.
- O tradutor interno cobre um conjunto definido de códigos comuns de fenômenos; códigos não cobertos são exibidos sem interpretação.
- A mensagem original permanece disponível mesmo quando alguma parte não puder ser interpretada.
