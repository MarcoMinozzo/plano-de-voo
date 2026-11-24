# Feature Specification: Clarear a tela do piloto

**Feature Branch**: `003-clarear-tela-piloto`

**Created**: 2026-11-14

**Status**: Draft

**Input**: User description: "Aplicar as melhorias de tela já avaliadas: o formulário guarda o que o piloto informou quando a conta recusa; o aeródromo é encontrado digitando identificador ou nome; a confirmação de hora no passado só aparece quando a hora já passou; o estado do plano e o item indisponível aparecem em português de planejamento; a tabela de grandezas só aparece quando tem linha; o aviso de que o mapa de ruas não é a carta fica junto do mapa, e a carta é identificável como carta de voo visual; um plano já feito pode ser alterado e recalculado; ao marcar o checklist, o item continua visível."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recuperar o voo quando a conta recusa (Priority: P1)

O piloto preenche origem, destino, hora, aeronave e os dados deste voo. A conta é recusada. A mensagem diz o que corrigir, e tudo o que ele já informou continua na tela. Ele corrige o campo e pede a conta de novo, sem recomeçar o voo.

**Why this priority**: Sem isso, cada recusa apaga o trabalho. As outras melhorias de leitura não compensam um formulário que esquece o voo.

**Independent Test**: Informar um voo que a conta recusa e conferir que a mensagem e os valores informados aparecem juntos. Corrigir só o campo citado e concluir.

**Acceptance Scenarios**:

1. **Given** um piloto no formulário de plano novo com origem, destino, hora, aeronave e dados deste voo preenchidos, **When** a conta é recusada, **Then** a mensagem de recusa aparece e cada valor informado continua visível no campo correspondente.
2. **Given** essa tela de recusa, **When** o piloto corrige só o que a mensagem pede e confirma, **Then** a conta segue com os demais valores que já estavam na tela.
3. **Given** uma hora de partida ainda no futuro, **When** o piloto abre o formulário, **Then** não vê o pedido para planejar uma hora que já passou.
4. **Given** uma hora de partida que já passou e a conta pede confirmação, **When** a tela de recusa aparece, **Then** o pedido de confirmação aparece junto da mensagem, e a hora informada continua visível.

---

### User Story 2 - Encontrar o aeródromo digitando (Priority: P1)

O piloto escolhe origem e destino digitando parte do identificador publicado ou do nome. Vê só os aeródromos de avião da emenda vigente que combinam com o que digitou. Escolhe um. Não percorre a lista do país inteiro.

**Why this priority**: Sem um jeito de achar o lugar, o plano nacional não é usável. O catálogo e a rota já existem; a escolha é o que trava o piloto.

**Independent Test**: Com a emenda vigente disponível, digitar parte de um identificador conhecido e escolher esse aeródromo como origem, sem ver a lista nacional completa.

**Acceptance Scenarios**:

1. **Given** a emenda vigente disponível e o campo de origem vazio, **When** o piloto ainda não digitou, **Then** a lista nacional completa não é o meio de escolha.
2. **Given** o piloto digita parte do identificador ou do nome de um aeródromo de avião da emenda, **When** a busca responde, **Then** vê esse aeródromo, com identificador e nome, e não vê lugar que não combina.
3. **Given** o texto não combina com nenhum aeródromo de avião da emenda, **When** a busca responde, **Then** o piloto vê que não há correspondência e nenhum lugar é inventado.
4. **Given** a emenda vigente indisponível, **When** o piloto abre o formulário, **Then** vê que o catálogo nacional está indisponível e não escolhe um lugar estimado.

---

### User Story 3 - Alterar um plano e recalcular (Priority: P1)

No plano já gravado, o piloto pede para alterar. Vê o mesmo formulário, preenchido com a origem, o destino, a hora, a aeronave e os dados deste voo daquele plano. Muda a hora ou um peso e confirma. O mesmo plano é recalculado. Outro piloto não abre essa alteração.

**Why this priority**: A spec do plano direto já promete editar. Sem a tela, o piloto só consegue apagar e começar de novo.

**Independent Test**: Gravar um plano, alterar o peso, confirmar e ver o mesmo plano com o resultado novo. Um segundo piloto não abre essa alteração.

**Acceptance Scenarios**:

1. **Given** um plano do piloto, **When** ele pede para alterar, **Then** vê os valores atuais desse plano, inclusive origem, destino, hora, aeronave e dados deste voo.
2. **Given** esse formulário, **When** ele muda a hora ou um peso e confirma, **Then** o mesmo plano mostra o resultado recalculado e o painel aponta para essa versão.
3. **Given** um piloto que não é o dono, **When** tenta alterar o plano, **Then** o acesso é recusado, sem revelar se o plano existe.

---

### User Story 4 - Ler o estado em português de planejamento (Priority: P2)

No painel e na tela do plano, o piloto lê se o plano é aceitável para planejamento ou não é aceitável. Quando não é, o motivo está na mesma vista. Onde um item falta, a palavra é "indisponível", com acento, a mesma da orientação.

**Why this priority**: "Calculado" não diz se o plano pode ser usado. A palavra sem acento parece um estado quebrado, não a falta de fonte.

**Independent Test**: Abrir o painel com um plano aceitável e outro não aceitável e ler os dois rótulos. Abrir um plano com vento indisponível e ler a palavra acentuada.

**Acceptance Scenarios**:

1. **Given** um plano aceitável para planejamento, **When** o piloto olha o painel e a tela do plano, **Then** lê "aceitável para planejamento" e não lê o rótulo interno da conta.
2. **Given** um plano que a conta não aceita, **When** o piloto olha o painel e a tela do plano, **Then** lê "não aceitável" e, na tela do plano, o motivo.
3. **Given** tempo, vento, carta, radar, catálogo ou pôr do sol sem dado, **When** o piloto lê esse item na tela, **Then** a palavra é "indisponível".

---

### User Story 5 - Ver só a tabela que tem o que ler (Priority: P2)

Uma rota com mais de um trecho mostra a tabela dos trechos. A tabela de grandezas do plano direto só aparece quando há grandeza para ler. Uma rota de um trecho só continua mostrando as grandezas, cada uma com unidade e fonte.

**Why this priority**: Uma tabela vazia no meio do plano faz o piloto procurar um número que não está lá.

**Independent Test**: Abrir um plano de um trecho e ver a tabela de grandezas. Abrir um plano com escala e não ver tabela de grandezas vazia.

**Acceptance Scenarios**:

1. **Given** um plano com grandezas calculadas, **When** o piloto abre a tela, **Then** vê cada grandeza com valor, unidade e fonte.
2. **Given** um plano cuja conta não traz grandeza avulsa, **When** o piloto abre a tela, **Then** a tabela de grandezas não aparece, e a tabela de trechos continua.

---

### User Story 6 - Não confundir o mapa de ruas com a carta (Priority: P2)

Ao lado do mapa de ruas, o piloto lê que aquele mapa só situa a rota e o radar e não substitui a carta de voo visual. A carta, quando a fonte entrega, é identificável como carta de voo visual, com a fonte. Quando não entrega, lê "indisponível".

**Why this priority**: O mapa de ruas está no centro da tela. Sem a frase ao lado, o piloto pode usá-lo como carta.

**Independent Test**: Abrir um plano e achar a frase do mapa de ruas junto do mapa. Achar a carta nomeada como carta de voo visual, ou a palavra "indisponível".

**Acceptance Scenarios**:

1. **Given** um plano com mapa de ruas, **When** o piloto olha o mapa, **Then** a frase de que ele não substitui a carta de voo visual está na mesma vista do mapa, não só no texto de orientação no fim da página.
2. **Given** a carta disponível, **When** o piloto procura a carta, **Then** vê que é a carta de voo visual e qual é a fonte.
3. **Given** a carta indisponível, **When** o piloto procura a carta, **Then** lê "indisponível" e nenhum mapa é apresentado como carta.

---

### User Story 7 - Marcar o checklist sem perder o item (Priority: P2)

O piloto marca ou desmarca um item do checklist. O item mostra se está marcado. Depois da ação, esse item continua visível, e o resto do plano continua na tela.

**Why this priority**: Recarregar e voltar ao topo faz o piloto perder o item que acabou de marcar.

**Independent Test**: Num plano com vários itens, marcar um item que não é o primeiro e continuar vendo esse item marcado, sem precisar procurá-lo de novo no topo.

**Acceptance Scenarios**:

1. **Given** um item ainda não marcado, **When** o piloto marca, **Then** o item passa a mostrar que está marcado e permanece visível.
2. **Given** um item marcado, **When** o piloto desmarca, **Then** o item passa a mostrar que não está marcado e permanece visível.
3. **Given** o checklist de um plano, **When** o piloto marca um item, **Then** os outros itens e o aviso de que o resultado não autoriza o voo continuam na tela.

---

### Edge Cases

- Recusa por catálogo indisponível, manual ausente, origem igual ao destino, lugar que não é aeródromo de avião, ou hora inválida: a mensagem aparece e o que o piloto já tinha informado continua na tela.
- Busca com um caractere só, ou só com espaço: a lista nacional completa não aparece.
- Dois aeródromos combinam com o mesmo texto: os dois aparecem, cada um com identificador e nome, e o piloto escolhe.
- Alterar um plano e a nova conta ser recusada: os valores da alteração continuam na tela, e o plano anterior não é substituído por uma conta recusada sem o piloto confirmar de novo o que a mensagem pede.
- Plano não aceitável por peso, com rota existente: o rótulo é "não aceitável" e o motivo do peso aparece.
- Plano sem trecho, gravado como não aceitável: não há tabela de grandezas vazia nem tabela de trechos vazia.
- Carta disponível sem o mapa de ruas poder ser desenhado: a carta continua identificável, e o aviso do mapa não afirma que o mapa está visível.
- Marcar o checklist de um plano de outro piloto: a ação é recusada e o item do outro piloto não muda.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Quando a conta de um plano novo ou de uma alteração é recusada, o piloto MUST ver a mensagem e MUST continuar vendo cada valor que informou.
- **FR-002**: O pedido para planejar uma hora que já passou MUST aparecer só quando a hora informada já passou.
- **FR-003**: Origem e destino MUST ser caixas de seleção. O piloto MUST poder reduzir a caixa digitando parte do identificador ou do nome, e a caixa MUST mostrar só os lugares que combinam. Com a emenda vigente, os lugares são os aeródromos de avião dessa emenda. Sem a emenda, a tela MUST dizer que o catálogo nacional está indisponível e a caixa MUST listar só os aeródromos já gravados na base, sem apresentá-los como o país inteiro.
- **FR-004**: Se o texto não combina com nenhum aeródromo de avião da emenda, o piloto MUST ver que não há correspondência. O sistema MUST NOT inventar lugar.
- **FR-005**: Com o catálogo nacional indisponível, o formulário MUST dizer isso e MUST NOT oferecer lugar estimado.
- **FR-006**: A partir de um plano seu, o piloto MUST poder abrir a alteração com os valores atuais e MUST poder recalcular o mesmo plano.
- **FR-007**: Outro piloto MUST NOT alterar esse plano. A recusa MUST NOT revelar se o plano existe.
- **FR-008**: No painel e na tela do plano, um plano aceitável para planejamento MUST aparecer como "aceitável para planejamento". Um plano que a conta não aceita MUST aparecer como "não aceitável", com o motivo na tela do plano.
- **FR-009**: Tempo, vento, carta, radar, catálogo e pôr do sol sem dado MUST ser lidos como "indisponível" na tela.
- **FR-010**: A tabela de grandezas MUST aparecer só quando há grandeza para ler. Cada grandeza mostrada MUST trazer valor, unidade e fonte.
- **FR-011**: A frase de que o mapa de ruas só situa a rota e o radar, e não substitui a carta de voo visual, MUST estar na mesma vista do mapa.
- **FR-012**: A carta disponível MUST ser identificável como carta de voo visual, com a fonte. A carta ausente MUST aparecer como "indisponível".
- **FR-013**: Marcar ou desmarcar um item do checklist MUST mostrar o novo estado e MUST manter esse item visível, com o resto do plano na tela.
- **FR-014**: A tela e o PDF MUST continuar avisando que o resultado não substitui o manual, o treinamento nem a norma, e não autoriza o voo.
- **FR-015**: Esta feature MUST NOT mudar a conta da rota, a reserva, o vento, o pôr do sol, o catálogo nem o isolamento entre pilotos. MUST NOT protocolar o plano.

### Key Entities

- **Valor informado**: o que o piloto digitou ou escolheu neste envio, e que permanece visível quando a conta recusa.
- **Correspondência de aeródromo**: aeródromo de avião da emenda vigente cujo identificador ou nome combina com o texto digitado.
- **Rótulo de planejamento**: o que o piloto lê no lugar do estado interno: aceitável para planejamento, ou não aceitável.
- **Item de checklist**: texto, fonte e se está marcado, permanecendo visível depois da marcação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das recusas de conta cobertas pelos cenários, os valores informados continuam visíveis junto da mensagem.
- **SC-002**: Com a emenda disponível, o piloto escolhe um aeródromo conhecido digitando parte do identificador, vendo só as correspondências, sem percorrer a lista nacional.
- **SC-003**: Em 100% dos planos do painel, o estado lido é "aceitável para planejamento" ou "não aceitável". Em 100% dos itens sem dado, a palavra lida é "indisponível".
- **SC-004**: Em 100% dos planos sem grandeza avulsa, a tabela de grandezas não aparece.
- **SC-005**: Em 100% dos planos que mostram o mapa de ruas, a frase de que ele não substitui a carta está na mesma vista do mapa.
- **SC-006**: Alterar peso ou hora de um plano próprio recalcula esse plano. Um segundo piloto não conclui a alteração.
- **SC-007**: Depois de marcar um item que não é o primeiro, esse item continua visível e mostra que está marcado.

## Assumptions

- O piloto já entra no espaço próprio. Cadastro, senha e sessão não mudam.
- "Parte do identificador ou do nome" exige texto além de um caractere e de espaço. Com menos que isso, nenhuma lista nacional aparece.
- A correspondência não distingue maiúsculas. O identificador publicado e o nome visível bastam para o piloto reconhecer o lugar.
- A alteração usa os mesmos campos do plano novo. Uma conta recusada na alteração não apaga o plano já gravado.
- O rótulo "aceitável para planejamento" não é autorização de voo. O aviso educacional permanece na tela e no PDF.
- "Indisponível" com acento é a palavra única para falta de fonte na tela. O PDF continua dizendo o mesmo sentido.
- Manter o item visível inclui voltar a esse item quando a tela é reapresentada. Não exige que a marcação aconteça sem reapresentar a tela.
- A conta da rota, a reserva de 30 minutos, o vento, o pôr do sol e o catálogo permanecem os das specs `001` e `002`.
