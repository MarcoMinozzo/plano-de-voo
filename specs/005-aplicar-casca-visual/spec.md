# Feature Specification: Aplicar a casca visual

**Feature Branch**: `005-aplicar-casca-visual`

**Created**: 2026-11-24

**Status**: Draft

**Input**: User description: "Revestir todas as telas com a planta da pista e o emblema Plano de Voo. A entrada, o cadastro e o plano novo ficam num card central de vidro azul acinzentado. Ao calcular, o card some e uma ampulheta diz Em processamento até a resposta. O plano calculado mantém um resumo acima das fichas. O menu traz Novo voo, Voos planejados, Imprimir voo e Sair. A tela estreita é uma coluna."

## Clarifications

### Session 2026-11-24

- Q: A ficha do plano e a lista de voos ficam no papel branco ou no vidro? → A: Todos os cards usam o mesmo vidro azul acinzentado, com texto branco.
- Q: Quanto o vidro desfoca a planta atrás do card? → A: Desfoque médio de 12 px, além dos 82% de opacidade.
- Q: O que fazer com texto longo e tabela larga em tela estreita? → A: O texto quebra a linha dentro do card, e a tabela larga rola na horizontal dentro do próprio card. A página não rola.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconhecer o produto em qualquer tela (Priority: P1)

O piloto abre qualquer tela e vê a mesma planta da pista e da torre ao fundo, com o emblema Plano de Voo como único logo. As cores visíveis são as do emblema: azul escuro, azul claro, amarelo e branco. O card é azul acinzentado e deixa a planta aparecer por trás. Numa tela estreita, a página é uma coluna, com o menu quebrando a linha e as abas das fichas rolando de lado.

**Why this priority**: Sem a mesma casca, a entrada e o plano parecem produtos diferentes. A tela estreita é a que o piloto leva no telefone.

**Independent Test**: Abrir a entrada, o cadastro, o plano novo, o plano calculado e a lista de voos, numa largura abaixo de 720 px e numa largura maior. Em todas, a planta e o emblema estão visíveis, e a estreita não exige rolagem horizontal da página.

**Acceptance Scenarios**:

1. **Given** qualquer tela do produto, **When** o piloto a abre, **Then** o fundo é a planta da pista e da torre e o único logo é o emblema Plano de Voo.
2. **Given** um card sobre essa planta, **When** o piloto olha o card, **Then** ele tem cantos arredondados, tom azul acinzentado, e a planta continua perceptível atrás dele.
3. **Given** uma largura abaixo de 720 px, **When** o piloto abre uma tela autenticada, **Then** o conteúdo fica numa coluna, o menu quebra em mais de uma linha e as abas das fichas rolam na horizontal.
4. **Given** uma largura de 720 px ou mais, **When** o piloto abre a entrada ou o plano novo, **Then** o card fica centrado e não estica até a borda da janela.

---

### User Story 2 - Entrar e informar o voo no mesmo vidro (Priority: P1)

O piloto entra, ou cria o acesso, num card central com o emblema. Depois de entrar, outro card central pede só os dados já exigidos para o cálculo: tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem. A frase de que o resultado apoia o planejamento e não autoriza o voo fica visível sem um clique.

**Why this priority**: A entrada é a primeira tela. O card do plano novo é o que o piloto preenche antes de qualquer ficha.

**Independent Test**: Abrir a entrada e o cadastro e conferir o mesmo card. Entrar e conferir os sete campos, nesta ordem, sem pedido de combustível a bordo nem de peso de piloto separado.

**Acceptance Scenarios**:

1. **Given** o produto fechado, **When** o piloto abre a entrada, **Then** vê o card de vidro com o emblema, identificação, senha e o caminho para criar acesso, sem o menu de voo.
2. **Given** a tela de criar acesso, **When** o piloto a compara com a entrada, **Then** o fundo, o emblema e o card são os mesmos.
3. **Given** uma entrada aceita, **When** o piloto vê o plano novo, **Then** o card pede os sete dados, na ordem já especificada, e a frase de que o resultado não autoriza o voo está visível.
4. **Given** identificação inexistente ou senha errada, **When** a entrada é recusada, **Then** a frase é a mesma nos dois casos e o card permanece com o que foi digitado.

---

### User Story 3 - Esperar o cálculo sem o card (Priority: P1)

O piloto pede o cálculo. O card some. Fica a ampulheta girando e a frase "Em processamento", nas cores do emblema, até o servidor responder. Se a conta recusa, a ampulheta sai e o card volta com os valores e o motivo. Se a conta aceita, o piloto vê o resumo e as fichas.

**Why this priority**: Sem essa espera, o piloto não sabe se o pedido saiu. Sem a volta do card, uma recusa apaga o que ele digitou.

**Independent Test**: Enviar um plano válido e ver a ampulheta no lugar do card até as fichas aparecerem. Enviar um plano recusado e ver o card de volta, com os mesmos valores.

**Acceptance Scenarios**:

1. **Given** um plano novo preenchido, **When** o piloto pede o cálculo, **Then** o card deixa de estar visível e a tela mostra a ampulheta com a frase "Em processamento".
2. **Given** a ampulheta visível, **When** a conta aceita, **Then** a ampulheta sai e o plano calculado aparece.
3. **Given** a ampulheta visível, **When** a conta recusa, **Then** a ampulheta sai, o card volta com os valores informados, inclusive as opções escolhidas, e o motivo fica visível.
4. **Given** a ampulheta visível, **When** o piloto pede Imprimir voo, **Then** nenhum documento é produzido enquanto a frase "Em processamento" permanece.

---

### User Story 4 - Manter o resumo e o menu (Priority: P2)

Acima das fichas de trecho, um card resume o voo inteiro. Cada linha nomeia um trecho pelos códigos de saída e de chegada e pelos números já calculados. Trocar a aba não troca esse resumo. O menu, visível depois da entrada, oferece Novo voo, Voos planejados, Imprimir voo e Sair.

**Why this priority**: O resumo é a leitura do voo todo enquanto a ficha mostra um trecho. O menu é o caminho para outro voo, para a lista e para a saída.

**Independent Test**: Abrir um plano com dois trechos, trocar a aba e ver o mesmo resumo. Usar cada item do menu uma vez.

**Acceptance Scenarios**:

1. **Given** um plano com mais de um trecho, **When** o piloto troca a aba, **Then** a ficha da frente muda e o card de resumo permanece com as mesmas linhas.
2. **Given** o menu, **When** o piloto escolhe Novo voo, **Then** volta o card vazio do plano novo.
3. **Given** o menu, **When** o piloto escolhe Voos planejados, **Then** vê só os próprios planos, cada um com origem, destino, partida e estado legível.
4. **Given** um plano aberto, **When** o piloto escolhe Imprimir voo, **Then** recebe o relatório desse plano.
5. **Given** nenhum plano aberto, **When** o piloto escolhe Imprimir voo, **Then** lê "Não há voo para imprimir." e continua na mesma tela.
6. **Given** uma sessão aberta, **When** o piloto escolhe Sair, **Then** a sessão encerra e a próxima tela é a entrada.

---

### Edge Cases

- Lista de voos vazia: a tela diz que não há voo planejado. Novo voo continua no menu.
- Plano de outro piloto: a lista, a ficha e a impressão não mostram esse voo.
- Sessão encerrada por sair ou por oito horas sem uso: a próxima tela é a entrada, sem o menu de voo.
- Senha de cadastro com menos de 8 caracteres: o acesso não é criado e o card permanece.
- Cinco recusas de entrada em 15 minutos: a mesma frase de recusa permanece por 15 minutos.
- Carta, radar, METAR ou grandeza sem dado: a ficha continua dizendo indisponível. Esta casca não preenche esse vazio.
- Durante "Em processamento", Novo voo e Voos planejados não abrem outra tela antes da resposta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Toda tela MUST mostrar a planta da pista e da torre como fundo e o emblema Plano de Voo como único logo.
- **FR-002**: As cores visíveis MUST ser as do emblema: azul escuro, azul claro, amarelo e branco. Todo card, inclusive a ficha do plano e a lista de voos planejados, MUST ser do mesmo vidro azul acinzentado, de cantos arredondados, com texto branco. O vidro MUST desfocar a planta atrás dele em 12 px e MUST deixá-la perceptível.
- **FR-003**: Abaixo de 720 px, a tela MUST ser uma coluna. O menu MUST quebrar a linha. As abas das fichas MUST rolar na horizontal. A página MUST NOT exigir rolagem horizontal. Nenhum texto MUST sair do card: o texto longo quebra a linha, e a tabela larga rola na horizontal dentro do próprio card. De 720 px para cima, o card de entrada e o de plano novo MUST ficar centrados, sem ocupar a largura inteira da janela.
- **FR-004**: A entrada e o cadastro MUST usar o mesmo card central, com o emblema. Essas duas telas MUST NOT mostrar o menu de voo. A recusa de entrada MUST usar a mesma frase para identificação inexistente e senha errada.
- **FR-005**: Depois de entrar, o plano novo MUST ser um card central com os sete campos já exigidos, nesta ordem: tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem. O card MUST NOT pedir combustível a bordo nem peso de piloto separado. A frase de que o resultado apoia o planejamento e não autoriza o voo MUST estar visível sem um clique.
- **FR-006**: Ao pedir o cálculo, o card MUST deixar de estar visível. A tela MUST mostrar uma ampulheta em movimento e a frase "Em processamento" até a resposta.
- **FR-007**: Se a conta recusa, a ampulheta MUST sair e o card MUST voltar com os valores informados, inclusive as opções das caixas, e com o motivo. Se a conta aceita, a ampulheta MUST sair e o plano calculado MUST aparecer.
- **FR-008**: Enquanto "Em processamento" estiver visível, Imprimir voo MUST NOT produzir documento, e Novo voo e Voos planejados MUST NOT abrir outra tela.
- **FR-009**: O plano calculado MUST mostrar, acima das fichas, um card de resumo que não muda quando a aba muda. Cada linha MUST nomear um trecho pelos códigos de saída e de chegada e pelos números já calculados. O resumo MUST NOT ensinar técnica de decolagem nem de pouso.
- **FR-010**: Depois da entrada, o menu MUST oferecer Novo voo, Voos planejados, Imprimir voo e Sair. Novo voo abre o card vazio. Voos planejados lista só os planos daquele piloto, com origem, destino, partida e estado. Imprimir voo, com um plano aberto, entrega o relatório desse plano. Sem plano aberto, a resposta visível MUST ser "Não há voo para imprimir." e a tela MUST permanecer. Sair encerra a sessão e volta à entrada.
- **FR-011**: Esta feature MUST NOT alterar a conta, os campos do plano novo, o conteúdo da ficha, o METAR nomeado por medida, a escolha entre carta de voo visual e mapa de ruas, o radar opcional, nem a regra de que o checklist fica só no relatório impresso, sem marcação. Essas regras permanecem as de `specs/004-enxugar-tela-piloto/spec.md`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das telas abertas, abaixo e acima de 720 px, a planta da pista e o emblema estão visíveis.
- **SC-002**: O piloto completa a entrada e encontra os sete campos do plano novo num único card, sem campo de combustível a bordo.
- **SC-003**: Entre o pedido de cálculo e a resposta, o card do formulário fica invisível e a frase "Em processamento" fica visível o tempo todo.
- **SC-004**: Num plano de dois trechos, trocar a aba muda a ficha da frente e deixa o resumo com as mesmas duas linhas.
- **SC-005**: Sem plano aberto, Imprimir voo mostra "Não há voo para imprimir." e não muda de tela. Com plano aberto, o piloto recebe um relatório desse plano.

## Assumptions

- O desenho fechado em `_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/` é a referência visual. O vidro usa 82% de opacidade e desfoque de 12 px, e o véu sobre a planta usa 35%. A especificação manda o piloto perceber a planta atrás do card. Esses dois percentuais são a medida acordada.
- 720 px é o corte entre a coluna estreita e o card centrado.
- A ampulheta usa o amarelo do emblema. A frase exata é "Em processamento".
- A frase exata sem plano aberto é "Não há voo para imprimir."
- O cadastro repete o card da entrada. Não ganha uma tela de referência separada.
- A lista de voos planejados e o relatório impresso não ganham desenho além do que esta especificação e a 004 já dizem.
- Não entra arquivo de fonte novo nem biblioteca visual nova. O texto continua em sans-serif e em português.
- As fichas, a carta, o radar, o METAR e o checklist da 004 já estão especificados. Esta feature só os veste e acrescenta o resumo, a espera e o menu.
