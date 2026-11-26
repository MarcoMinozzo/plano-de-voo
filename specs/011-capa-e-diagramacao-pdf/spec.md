# Feature Specification: Capa e diagramação do PDF de voo

**Feature Branch**: `011-capa-e-diagramacao-pdf`

**Created**: 2026-11-25

**Status**: Draft

**Input**: Melhorar a apresentação do PDF, que hoje é texto corrido sem capa; incluir o emblema, nome do usuário, rota do voo e data.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identificar e consultar o relatório do voo (Priority: P1)

Como piloto, quero baixar um relatório técnico bem diagramado, com uma capa
identificando meu voo, para localizar seus dados, fontes e avisos com facilidade.

**Why this priority**: O PDF é a versão imprimível do planejamento; uma
apresentação clara ajuda o piloto a identificar o documento e consultar seu
conteúdo sem confundir estimativas, dados ausentes e informações confirmadas.

**Independent Test**: Cadastrar ou atualizar o nome de exibição, gerar um PDF
para um plano próprio e conferir capa e corpo num voo direto e num voo com
escalas.

**Acceptance Scenarios**:

1. **Given** um piloto autenticado e seu plano, **When** solicita o PDF,
   **Then** a capa mostra o emblema, o nome de exibição, a rota completa em
   ordem e a data e hora de partida registradas.
2. **Given** um cadastro novo ou perfil próprio, **When** o piloto informa
   nome válido, **Then** o nome é salvo e pode ser alterado; contas anteriores
   à mudança recebem a identificação existente como valor inicial.
3. **Given** um plano extenso, dados DEMO ou fontes indisponíveis, **When** o
   PDF é gerado, **Then** as páginas permanecem legíveis e preservam fontes,
   estados indisponíveis, avisos, checklist sugerido e orientação do piloto.
4. **Given** um plano ou perfil de outro piloto, **When** alguém tenta acessar
   o PDF ou editar o perfil, **Then** a ação é recusada.

### Edge Cases

- Nome vazio, só com espaços ou acima de 160 caracteres.
- Conta existente sem nome de exibição antes da migração.
- Rota com várias escalas, referências longas e conteúdo que cruza páginas.
- Plano com dados técnicos sintéticos ou meteorologia, vento ou carta indisponível.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST solicitar um nome de exibição ao criar uma conta
  e MUST permitir que o piloto autenticado altere somente o próprio nome.
- **FR-002**: O nome MUST ser aparado, obrigatório e conter no máximo 160
  caracteres. Valores vazios ou maiores MUST ser recusados sem persistência.
- **FR-003**: Contas existentes MUST receber a identificação de acesso atual
  como valor inicial de nome de exibição, sem alterar identificação ou senha.
- **FR-004**: A capa do PDF MUST mostrar o emblema e o nome do produto, o nome
  atual do piloto, a sequência completa de origem, escalas e destino, e a data
  e hora de partida do plano.
- **FR-005**: O relatório MUST organizar os dados em seções legíveis, com
  hierarquia tipográfica, espaçamento, cabeçalhos e paginação, sem cortar ou
  sobrepor conteúdo.
- **FR-006**: O PDF MUST preservar os dados, unidades e fontes já apresentados,
  a documentação do piloto e o aviso de que o resultado não autoriza o voo.
- **FR-007**: Estimativas didáticas e dados sintéticos MUST continuar claramente
  identificados; indisponibilidades MUST permanecer explícitas. O checklist
  sugerido MUST NOT mostrar se os itens foram marcados.
- **FR-008**: O PDF MUST continuar acessível somente ao piloto dono do plano;
  perfil de outra pessoa MUST NOT ser consultável ou editável pela sessão atual.
- **FR-009**: O sistema MUST NOT alterar cálculos, dados do plano, meteorologia
  ou regras de voo para formatar o documento.

### Key Entities

- **Perfil do piloto**: nome de exibição e identificação de acesso independente;
  somente o próprio piloto pode atualizar seu nome.
- **Plano de voo**: rota ordenada, data e hora de partida, resultados,
  procedência, estados de disponibilidade e checklist sugerido.
- **Relatório PDF**: documento do plano, com capa e conteúdo paginado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos testes, a capa exibe emblema, nome atual do piloto,
  rota ordenada completa e data/hora de partida.
- **SC-002**: Todos os cenários de cadastro, alteração do nome e migração de
  contas existentes passam sem alterar credenciais de acesso.
- **SC-003**: Em 100% dos PDFs de teste com escalas, conteúdo longo, DEMO ou
  indisponibilidade, informações e avisos são legíveis, sem corte ou sobreposição.
- **SC-004**: Em 100% das tentativas de outro piloto, PDF e edição de perfil
  permanecem inacessíveis.

## Assumptions

- A data da capa é a data e hora de partida planejadas, não a data de geração
  do arquivo; o fuso será indicado conforme os dados do plano.
- A sequência de rota usa os trechos calculados, incluindo escalas, sem
  recalcular ou simplificar o resultado.
- O emblema existente é a marca oficial do documento.
- O conteúdo e os avisos atuais do PDF continuam necessários; a mudança é de
  apresentação e do nome de exibição, não do cálculo.
- Nenhuma biblioteca adicional é necessária.
- A validação inclui testes automatizados de perfil, migração, acesso e conteúdo
  do PDF, além de inspeção visual de páginas A4.
