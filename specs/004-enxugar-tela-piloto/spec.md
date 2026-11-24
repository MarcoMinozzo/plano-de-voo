# Feature Specification: Enxugar a tela do piloto

**Feature Branch**: `004-enxugar-tela-piloto`

**Created**: 2026-11-14

**Status**: Draft

**Input**: User description: "Corrigir o excesso de informação e a visualização ruim. Deixar a interface mais fácil de usar, limpa, profissional e moderna, como a releitura da tela: caixas de seleção fechadas com as opções dentro, formulário em dois grupos, aviso curto, texto longo atrás de um pedido de leitura, resultado com estado na frente, tabela sem repetir unidade e fonte em cada célula, dados ausentes numa linha só, mapa só quando há rota."

## Clarifications

### Session 2026-11-23

- Q: O peso que o piloto informa é o das pessoas, incluindo o piloto, separado do peso da bagagem? → A: Sim. O número de passageiros inclui o piloto. O peso das pessoas é o total informado, não um peso por pessoa multiplicado pela quantidade. A bagagem é outro peso. O combustível a bordo não é pedido; usa o combustível de planejamento já gravado no manual da aeronave.
- Q: A lista de tipo de avião reúne todos os aviões apenas de voo visual? → A: Não. O plano segue sendo de voo visual diurno. A lista é a dos modelos de avião pequeno do extrato público do Registro Aeronáutico Brasileiro, com peso máximo de decolagem aprovado igual ou inferior a 5.670 kg. Helicóptero, planador, balão e avião grande ficam de fora. A ordem é a frota desse extrato, da maior para a menor. Número técnico vem só do manual oficial do modelo. Modelo sem manual aparece e o cálculo é recusado, dizendo qual manual falta. É proibido inventar modelo, peso, velocidade ou consumo.
- Q: Origem e destino passam a incluir todos os aeródromos oficiais do Brasil por uma lista escrita nesta feature? → A: Não. Origem e destino são os aeródromos de avião da emenda vigente do ROTAER, obtidos pela área rotaer do AISWEB, cada um com identificador, nome, coordenada, elevação e a emenda de onde saiu. Heliponto não entra. Sem essa emenda, o catálogo nacional fica indisponível; a tela pode mostrar os aeródromos já gravados e MUST dizer que a lista é local e não é o catálogo do país. É proibido completar com coordenada estimada ou tratar a semente de sete indicativos como o Brasil. Esta feature não carrega nem substitui esse catálogo. A carga permanece a de `specs/002-rota-com-escalas/`.
- Q: O texto da origem e do destino deve achar o aeródromo por um pedaço do código ou do nome que já aparece na caixa, ou também pelo nome da cidade publicado no ROTAER? → A: Um texto só. Vale parte do código ou parte do nome do aeródromo que a caixa mostra. A comparação ignora maiúsculas e acentos. A cidade que não esteja nesse nome não entra. O texto não cria um lugar fora da caixa.

### Session 2026-11-24

- Q: Na tela do plano calculado, o checklist sai da tela e fica só no PDF, e cada trecho vira uma ficha com carta náutica ou mapa de ruas e radar de chuva, no lugar da tabela única e do mapa de ruas atuais? → A: Sim. O checklist sai da tela e fica só no PDF. Cada trecho vira uma ficha, com carta ou mapa de ruas e com o radar de chuva opcional. Quando o piloto escolhe o mapa de ruas, a frase de que ele não substitui a carta de voo visual permanece ao lado do mapa. A conta, a unidade, a fonte, o dado indisponível e a frase de que o resultado não autoriza o voo continuam.
- Q: A carta que o piloto escolhe na ficha é a carta de voo visual que o plano já busca, ou uma carta náutica marítima de outra fonte? → A: É a carta de voo visual que o plano já mostrava, com a fonte gravada. Sem esse dado, a ficha diz indisponível e não desenha outra carta no lugar.
- Q: O texto depois do mapa é a sequência já calculada do trecho, ou uma recomendação nova de como decolar e pousar? → A: É a sequência já calculada daquele trecho: de qual aeródromo sai, em qual chega, e os números que a conta já gravou. Não acrescenta técnica de decolagem nem de pouso.
- Q: Sem o checklist na tela, o piloto ainda marca os itens em algum lugar? → A: Não. O PDF imprime a lista sugerida, com o texto e a fonte de cada item. O aplicativo não oferece marcar nem desmarcar.
- Q: O METAR na ficha mostra o texto já gravado de cada aeródromo do trecho, com um campo só para a medida que esse texto contém, ou um conjunto fixo de campos mesmo quando o boletim não traz a medida? → A: Dois METAR, o da saída e o da chegada, a partir do texto já gravado. Cada medida presente nesse texto ganha um campo com o nome dela. Medida ausente fica indisponível. Nenhum valor é inventado.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escolher o voo numa tela curta (Priority: P1)

O piloto abre um plano novo e informa só o que é deste voo: tipo de avião, origem, destino, data e hora, número de passageiros e dois pesos, o das pessoas e o da bagagem. O tipo de avião, a origem e o destino aparecem como caixas de uma linha, já mostrando um nome real. O combustível a bordo e um peso de piloto separado não aparecem. O combustível usado na conta é o de planejamento do manual. Uma frase diz que a lista local não é o país inteiro, quando for o caso. Outra frase diz que o resultado não autoriza o voo.

**Why this priority**: É a tela que o piloto acabou de recusar. Sem ela curta e com opções visíveis no campo, o resto da leitura não importa.

**Independent Test**: Abrir o plano novo com uma aeronave e alguns aeródromos gravados e conferir que só existem os campos deste voo, as caixas de uma linha e as duas frases. Enviar o voo sem informar combustível e receber a conta, ou a recusa com os valores ainda nos campos.

**Acceptance Scenarios**:

1. **Given** ao menos uma aeronave com manual gravado e ao menos dois aeródromos oferecidos, **When** o piloto abre o plano novo, **Then** a caixa da aeronave mostra o nome de uma aeronave, a caixa de origem mostra um aeródromo e a caixa de destino mostra outro, cada uma em uma linha, e abrir a caixa lista as opções.
2. **Given** essa tela, **When** o piloto olha o formulário, **Then** vê só estes campos, nesta ordem: tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem, e o pedido de calcular no fim. Não vê combustível a bordo nem peso de piloto separado.
3. **Given** doze aeródromos ou menos, **When** o piloto abre o plano novo, **Then** não há campo extra para filtrar a lista.
4. **Given** mais de doze aeródromos, **When** o piloto digita um pedaço do código ou do nome do aeródromo que a caixa mostra, **Then** a caixa continua no lugar e só mostra as opções em que esse pedaço aparece no código ou no nome, sem distinguir maiúsculas nem acentos.
5. **Given** a lista é a dos aeródromos já gravados e não a emenda nacional, **When** o piloto abre o plano novo, **Then** uma frase diz que a lista é local e não é o catálogo do país inteiro.
6. **Given** qualquer plano novo ou alteração, **When** a tela abre, **Then** uma frase visível diz que o resultado apoia o planejamento e não autoriza o voo, e o texto longo de orientação não ocupa a tela aberta.

---

### User Story 2 - Ler o plano sem repetir o que já foi dito (Priority: P1)

O piloto abre um plano calculado e a primeira leitura é a rota e se ele é aceitável para planejamento. Cada trecho é uma ficha. A aba mostra o código do aeródromo de saída e o de chegada. Clicar na aba traz essa ficha para a frente. Na ficha, a unidade fica no título quando a grandeza usa a mesma em todo o trecho, e a fonte gravada aparece uma vez. Tempo, vento, carta e radar ausentes continuam nomeados, sem valor inventado. O mapa do trecho só aparece quando a rota tem ao menos dois pontos. O piloto escolhe a carta de voo visual que o plano já mostrava, ou o mapa de ruas, e pode sobrepor ou não o radar de chuva. No mapa de ruas, a frase de que ele não substitui a carta de voo visual fica ao lado do mapa. Sem a carta, a ficha diz indisponível e não desenha outra no lugar. Depois do mapa, a ficha repete a sequência calculada daquele trecho: o aeródromo de saída, o de chegada e os números já gravados. Esse texto não ensina a decolar nem a pousar. A ficha também mostra o METAR já gravado da saída e o da chegada. Cada medida que esse texto contém aparece num campo com o nome dela. Medida que o texto não traz fica indisponível. Sem texto de METAR, o bloco daquele aeródromo diz indisponível.

**Why this priority**: O plano calculado é o que o piloto leva para a preparação. Uma tabela única e quatro frases de indisponível escondem o trecho que ele quer ler.

**Independent Test**: Abrir um plano com dois trechos e com tempo, vento, carta e radar indisponíveis. Conferir o estado na frente, uma ficha por trecho, a unidade no título, a fonte uma vez e a ausência nomeada sem valor inventado. Trocar a aba e ver a outra ficha na frente. No mapa de ruas, conferir a frase da carta ao lado do mapa.

**Acceptance Scenarios**:

1. **Given** um plano calculado, **When** o piloto abre a tela, **Then** o título é a rota e a linha seguinte é o estado em português de planejamento, com o nome da aeronave.
2. **Given** um trecho cuja distância, proa, tempo e combustível usam unidade conhecida, **When** o piloto lê a ficha, **Then** a unidade está no título da grandeza e o valor traz o número. A fonte gravada de cada grandeza aparece uma vez nessa ficha.
3. **Given** um valor cuja unidade ou fonte difere da usada no título, **When** o piloto lê esse valor, **Then** ele mostra também a unidade e a fonte daquele valor.
4. **Given** tempo, vento, carta e radar todos indisponíveis, **When** o piloto abre a ficha, **Then** vê esses quatro nomeados como indisponíveis, sem valor inventado e sem o mapa de ruas apresentado como carta.
5. **Given** ao menos um desses quatro com dado, **When** o piloto abre a ficha, **Then** o dado aparece por extenso e os ausentes são nomeados.
6. **Given** a rota tem ao menos dois pontos e a carta de voo visual está disponível, **When** o piloto abre a ficha do trecho, **Then** pode escolher essa carta ou o mapa de ruas e ligar ou desligar o radar de chuva sobre a escolha. A carta mostra a fonte gravada. No mapa de ruas, a frase de que ele não substitui a carta de voo visual está ao lado do mapa.
7. **Given** a rota não tem dois pontos, **When** o piloto abre o plano, **Then** o mapa não aparece.
8. **Given** dois trechos, **When** o piloto clica a aba do segundo, **Then** a ficha desse trecho vem para a frente e a primeira deixa de ser a ficha da frente.
9. **Given** o piloto quer o texto de orientação, **When** pede "Como ler este plano", **Then** vê o texto do piloto, inclusive o que informar, o que significa item indisponível e que o resultado não é autorização de voo. O PDF continua com esse texto.
10. **Given** uma ficha com mapa, **When** o piloto lê o texto depois do mapa, **Then** vê o aeródromo de saída, o de chegada e os números já gravados daquele trecho, e não vê técnica de decolagem nem de pouso.
11. **Given** METAR gravado na saída e na chegada, **When** o piloto lê a ficha, **Then** vê dois blocos, e cada medida presente no texto de um bloco aparece num campo com o nome dessa medida.
12. **Given** uma medida que o texto do METAR não traz, **When** o piloto lê esse campo, **Then** ele diz indisponível e não mostra valor inventado.
13. **Given** um aeródromo do trecho sem texto de METAR, **When** o piloto lê a ficha, **Then** o bloco desse aeródromo diz indisponível.

---

### User Story 3 - Levar o checklist só no PDF (Priority: P2)

O piloto não vê o checklist na tela do plano. O PDF imprime a lista sugerida, com o texto e a fonte de cada item. Não há ação de marcar nem de desmarcar, e o PDF não diz "marcado" nem "não marcado".

**Why this priority**: A tela fica para a rota e as fichas. A lista de conferência vai no documento impresso, sem um controle de marcação.

**Independent Test**: Abrir um plano com itens de checklist e confirmar que a tela não mostra esses itens nem um controle de marcar. Abrir o PDF e encontrar o texto e a fonte de cada item, sem a palavra marcado.

**Acceptance Scenarios**:

1. **Given** um plano com itens de checklist, **When** o piloto abre a tela, **Then** nenhum item de checklist aparece e não há ação de marcar.
2. **Given** esse plano, **When** o piloto pede o PDF, **Then** o PDF traz o texto e a fonte de cada item.
3. **Given** esse PDF, **When** o piloto lê os itens, **Then** não vê "marcado" nem "não marcado".

---

### Edge Cases

- Nenhuma aeronave com manual gravado: a caixa fica vazia e a frase de que não há aeronave continua visível. O cálculo segue recusado como hoje.
- Um único aeródromo: origem e destino mostram esse mesmo aeródromo. A conta continua recusando origem igual ao destino.
- Lista local e lista da emenda nacional usam a mesma caixa. Só a frase da lista local muda.
- Texto de filtro que não é parte do código nem do nome mostrado não cria aeródromo. A caixa não oferece esse lugar. A cidade que não esteja no nome mostrado não conta como acerto.
- Hora no passado: o pedido de confirmação continua aparecendo só quando a hora já passou.
- Número de passageiros menor que 1: a conta é recusada, porque o piloto entra nessa quantidade.
- Peso das pessoas ou peso da bagagem ausente: a conta é recusada. Nenhum dos dois é completado com valor estimado.
- O peso das pessoas é o total digitado. A quantidade de passageiros não multiplica esse peso.
- O combustível de planejamento ausente no manual: a conta é recusada e o nome do dado que falta é informado, como já ocorre com os outros números do manual.
- Recusa da conta: os valores informados continuam nos campos, inclusive a opção escolhida nas caixas.
- Plano de outro piloto: a alteração continua recusada, sem mostrar o voo alheio.
- Tabela de grandezas vazia: continua omitida.
- Painel: continua a lista curta de origem, destino, partida e estado legível. Ganha o mesmo visual das outras telas, sem coluna nova.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Tipo de avião, origem e destino MUST ser caixas de seleção de uma linha. A caixa fechada MUST mostrar um nome real quando existir opção. As opções MUST ser as que o catálogo já oferece: com a emenda vigente do ROTAER gravada, origem e destino listam os aeródromos de avião dessa emenda; com o extrato do RAB gravado, o tipo de avião lista os modelos de avião pequeno desse extrato. Sem essas publicações, a caixa lista só o que já está gravado e a frase da lista local permanece. Esta feature MUST NOT inventar aeródromo, modelo ou número de manual.
- **FR-002**: Com doze aeródromos ou menos, a tela MUST NOT mostrar campo de filtro. Com mais de doze, cada caixa de aeródromo MUST ter um campo de texto que reduz as opções sem substituir a caixa. O texto MUST manter a opção quando for parte do código ou parte do nome do aeródromo já exibido nessa opção. A comparação MUST ignorar maiúsculas e acentos. A cidade que não esteja nesse nome MUST NOT ser exigida. O texto MUST NOT aceitar um lugar que não esteja na caixa.
- **FR-003**: O formulário MUST ser uma lista simples, no visual da primeira tela, com o pedido de calcular no fim. Os únicos campos MUST ser, nesta ordem: tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas em quilogramas e peso da bagagem em quilogramas. O número de passageiros MUST incluir o piloto e MUST ser no mínimo 1. O peso das pessoas MUST incluir o piloto e MUST ser o total informado. A tela MUST NOT pedir combustível a bordo nem um peso de piloto separado. MUST NOT usar cartão, grupo visual nem botão estilizado no lugar do controle nativo.
- **FR-004**: Quando a lista não é a emenda nacional, a tela MUST mostrar uma frase de que a lista é local e não é o catálogo do país inteiro.
- **FR-005**: Formulário e plano MUST mostrar, sem o piloto abrir nada, uma frase de que o resultado apoia o planejamento e não autoriza o voo.
- **FR-006**: O texto completo de orientação do piloto MUST permanecer na tela do plano, atrás do pedido "Como ler este plano", e MUST permanecer no PDF. A tela aberta MUST NOT começar nem terminar com esse texto inteiro à vista.
- **FR-007**: A tela do plano MUST abrir com a rota, o estado em português de planejamento e o nome da aeronave.
- **FR-008**: Cada trecho MUST ser uma ficha, com a aba nomeada pelos códigos dos aeródromos de saída e de chegada. Clicar na aba MUST trazer essa ficha para a frente. Na ficha, a unidade MUST estar no título da grandeza quando for a mesma nesse trecho, e a fonte gravada de cada grandeza MUST aparecer uma vez. Unidade ou fonte diferente MUST aparecer junto daquele valor.
- **FR-009**: Tempo, vento, carta e radar, quando indisponíveis, MUST ser nomeados como indisponíveis, sem valor inventado. Dado presente MUST aparecer por extenso. O mapa de ruas MUST NOT ser apresentado como carta.
- **FR-010**: O mapa do trecho MUST aparecer só quando a rota tem ao menos dois pontos. O piloto MUST poder escolher a carta de voo visual já obtida para o plano, ou o mapa de ruas, e MUST poder ligar ou desligar o radar de chuva sobre a escolha. A carta disponível MUST mostrar a fonte gravada. Sem a carta, a ficha MUST dizer indisponível e MUST NOT desenhar outra carta no lugar. No mapa de ruas, a frase de que ele não substitui a carta de voo visual MUST estar ao lado do mapa.
- **FR-011**: A tela do plano MUST NOT mostrar o checklist nem uma ação de marcar ou desmarcar. O PDF MUST trazer o texto e a fonte de cada item da lista sugerida. O PDF MUST NOT mostrar "marcado" nem "não marcado".
- **FR-014**: Depois do mapa, a ficha MUST repetir a sequência calculada daquele trecho: aeródromo de saída, aeródromo de chegada e os números já gravados. Esse texto MUST NOT acrescentar técnica de decolagem nem de pouso. Sem mapa, a mesma sequência MUST continuar visível na ficha.
- **FR-015**: A ficha MUST mostrar o METAR já gravado do aeródromo de saída e o do aeródromo de chegada, em blocos separados. Cada medida presente nesse texto MUST aparecer num campo com o nome dela e o valor lido do texto. Medida ausente nesse texto MUST ficar indisponível. Sem texto de METAR para um aeródromo, o bloco dele MUST dizer indisponível. A ficha MUST NOT inventar medida nem valor.
- **FR-012**: Recusa, alteração do próprio plano, isolamento entre pilotos, rótulo do painel, omissão da tabela de grandezas vazia e confirmação de hora no passado MUST continuar como na tela já entregue.
- **FR-013**: A conta da carga MUST somar o peso vazio da aeronave, o peso das pessoas informado, o peso da bagagem informado e o peso do combustível de planejamento. Esse combustível MUST ser o valor já gravado no manual da aeronave, com a unidade e a fonte já gravadas. A rota, a reserva, o vento, o pôr do sol e o isolamento do piloto MUST permanecer como estão. O catálogo nacional MUST permanecer o de `specs/002-rota-com-escalas/`: a emenda vigente do ROTAER e o extrato público do RAB, carregados fora desta feature. O PDF MUST continuar nomeando unidade e fonte em cada grandeza impressa.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: No plano novo, o piloto vê o nome da aeronave e um aeródromo de origem e outro de destino sem rolar uma lista aberta e sem ler o texto longo de orientação.
- **SC-002**: No plano novo, o piloto completa a conta informando só tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem. Combustível a bordo e peso de piloto separado não aparecem.
- **SC-003**: Num plano com os quatro dados externos indisponíveis, cada ficha nomeia essa ausência sem valor inventado e não repete a mesma fonte dentro da ficha.
- **SC-004**: O texto de que o resultado não autoriza o voo continua visível na tela e no PDF, e o texto de orientação continua acessível na tela do plano em um passo ("Como ler este plano").
- **SC-005**: A tela do plano não mostra o checklist nem um controle para marcá-lo. O PDF traz o texto e a fonte de cada item e não diz se está marcado.

## Assumptions

- Doze aeródromos é o limite em que a caixa fechada ainda se abre com conforto. Acima disso, o filtro volta, sem voltar a lista aberta na página. O filtro usa o código e o nome que a opção já mostra.
- Quando o piloto ainda não escolheu, a origem mostra o primeiro aeródromo da lista e o destino mostra o segundo, se houver dois. A escolha já gravada ou recusada prevalece.
- "Moderna" aqui é hierarquia, espaço e uma ação principal. Não entra biblioteca visual nova nem tema configurável.
- O painel, a entrada e o cadastro acompanham o mesmo visual, sem mudar o que o piloto faz neles.
- A rota, a reserva, o vento, o pôr do sol e o PDF detalhado ficam. A carga passa a usar o peso das pessoas, a bagagem e o combustível de planejamento do manual.
- Um plano já gravado com peso de piloto e peso de passageiro separados mostra, na alteração, a soma desses dois como peso das pessoas e mantém a bagagem. O combustível antigo não volta para o formulário.
- "Apenas por voo visual" não cria outra lista de aviões. O tipo de avião é o modelo pequeno do extrato do RAB. Origem e destino são os aeródromos de avião da emenda vigente do ROTAER. Sem a chave do AISWEB e sem o arquivo do extrato, ambos fora do repositório, essas listas não são gravadas e a frase de lista local continua.
