# Feature Specification: Rota com escalas

**Feature Branch**: `002-rota-com-escalas`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Devemos ter todos os aeródromos brasileiros cadastrados. Devemos ter todas as aeronaves de pequeno porte cadastradas, principalmente as mais usadas. O sistema deve otimizar e escolher a melhor rota a partir da origem e do destino e calcular todas as escalas necessárias, com base na documentação oficial e nas melhores práticas de voo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Usar qualquer aeródromo brasileiro (Priority: P1)

O piloto escolhe a origem e o destino entre os aeródromos de avião publicados na emenda vigente da lista oficial brasileira. Um heliponto não entra nessa lista. Se a publicação vigente não puder ser consultada, o piloto vê que o catálogo nacional está indisponível e nenhum aeródromo é inventado para completar a lista.

**Why this priority**: Sem o catálogo nacional, a rota não pode sair de qualquer aeródromo brasileiro nem pousar numa escala real.

**Independent Test**: Com a publicação vigente disponível, um aeródromo de avião que não estava na semente antiga pode ser origem ou destino. Um heliponto não pode. Sem a publicação, o plano não é calculado e a mensagem diz que o catálogo está indisponível.

**Acceptance Scenarios**:

1. **Given** a publicação vigente de aeródromos, **When** o piloto abre a origem, **Then** a lista contém os aeródromos de avião dessa emenda, cada um com o identificador publicado, e não contém heliponto.
2. **Given** um aeródromo de avião dessa emenda que não era um dos sete indicativos antigos, **When** o piloto o usa como origem ou destino, **Then** o plano aceita o lugar e mostra a fonte da coordenada.
3. **Given** a publicação vigente indisponível, **When** o piloto tenta montar o plano, **Then** o cálculo não segue e a tela diz que o catálogo nacional está indisponível, sem coordenada estimada.

---

### User Story 2 - Escolher um avião pequeno com manual (Priority: P1)

O piloto escolhe o modelo do avião. O catálogo cobre os modelos de avião pequeno que constam do registro público de aeronaves. Os modelos com mais aeronaves nesse registro vêm primeiro e, para a rota poder ser oferecida de forma útil, os modelos que somam a maior parte da frota têm o manual oficial gravado. Um modelo sem manual aparece na lista, mas o cálculo é recusado e diz qual manual falta. Peso, velocidade e consumo não são inventados.

**Why this priority**: A escala depende do alcance e do combustível do manual. Sem o manual, não há rota honesta.

**Independent Test**: Um modelo com manual gravado calcula o plano e cada número mostra a fonte do manual. Um modelo do registro sem manual não calcula e nomeia o manual ausente. Um avião acima do limite de avião pequeno não entra no catálogo.

**Acceptance Scenarios**:

1. **Given** o registro público de aeronaves, **When** o piloto abre a lista de modelos, **Then** vê os modelos de avião pequeno desse registro, com os de maior frota no topo.
2. **Given** um modelo com manual oficial gravado, **When** o piloto conclui o plano, **Then** navegação, combustível e limites saem desse manual, com unidade e fonte.
3. **Given** um modelo do registro sem manual gravado, **When** o piloto tenta concluir o plano, **Then** o sistema recusa o cálculo e diz qual manual falta.

---

### User Story 3 - Receber a melhor rota e as escalas (Priority: P1)

O piloto informa origem, destino e hora. O sistema escolhe a rota. Se o voo direto cabe no manual e na reserva do voo visual diurno, a rota não tem escala. Se não cabe, o sistema inclui só as escalas necessárias, em aeródromos de avião da publicação vigente, e mostra cada trecho. A rota escolhida é a de menor tempo de voo. Se duas rotas levam o mesmo tempo, fica a de menos escalas. Se o empate continuar, fica a mais curta. Se nenhuma rota cumprir a regra, o plano mostra o motivo e não aparece como aceitável.

**Why this priority**: É o pedido central: não deixar o piloto refazer a conta da escala.

**Independent Test**: Num par em que o direto ultrapassa o combustível de planejamento mais a reserva de 30 minutos, o plano volta com pelo menos uma escala e cada trecho dentro da regra, ou volta inaceitável dizendo por que não há rota. Nenhuma escala fica fora do catálogo.

**Acceptance Scenarios**:

1. **Given** origem, destino e um avião cujo manual permite o direto com a reserva diurna, **When** o piloto pede o plano, **Then** a rota tem um trecho só, da origem ao destino, com tempo, combustível, unidade e fonte.
2. **Given** um direto que não cabe no combustível de planejamento mais a reserva de 30 minutos, **When** o piloto pede o plano, **Then** a rota inclui as escalas necessárias, cada trecho cumpre a mesma regra, e a rota é a de menor tempo total.
3. **Given** nenhuma sequência de aeródromos publicados deixa todos os trechos dentro da regra, **When** o piloto pede o plano, **Then** o plano não aparece como aceitável e diz qual limite impediu a rota.

---

### User Story 4 - Ler a rota na tela e no PDF (Priority: P2)

Na tela e no PDF o piloto vê cada trecho, a hipótese de reabastecer em cada escala até o combustível de planejamento do manual, o que ficou indisponível e o aviso de que o resultado não autoriza o voo. O mapa desenha os trechos já calculados. Não há conta de navegação no navegador.

**Why this priority**: A rota só é útil se o piloto conseguir conferir trecho a trecho e imprimir.

**Independent Test**: O PDF de um plano com escala contém origem, cada escala, destino, horário, combustível de cada trecho, a hipótese de reabastecimento e o aviso de que não é autorização.

**Acceptance Scenarios**:

1. **Given** um plano com escala, **When** o piloto abre a tela, **Then** vê a ordem dos trechos, o combustível de cada um e a fonte de cada grandeza.
2. **Given** o mesmo plano, **When** o piloto pede o PDF, **Then** o documento repete os trechos, a hipótese de reabastecimento e o aviso de que não substitui o manual, o treinamento nem a norma, e não autoriza o voo.

---

### Edge Cases

- Origem e destino iguais: o plano não é calculado e diz que os lugares precisam ser diferentes.
- Identificador ausente da emenda vigente, ou lugar publicado só como heliponto: o plano não usa esse lugar e diz que não é aeródromo de avião na publicação vigente.
- Publicação de aeródromos indisponível: nada é calculado e nenhum indicativo antigo é tratado como lista nacional.
- Modelo sem manual, ou aeronave que não é avião pequeno: o cálculo é recusado e o motivo nomeia o manual ou o limite de porte.
- Vento oficial ausente no trecho: o trecho não ganha componente de vento. O item vento fica indisponível. A rota não assume vento de cauda.
- Hora de nascer ou pôr do sol indisponível: o plano não afirma que o voo cabe no dia. O item fica indisponível.
- Um trecho chegaria depois do pôr do sol no aeródromo de chegada desse trecho: esse trecho não entra numa rota aceitável de voo visual diurno.
- Em cada escala o plano assume reabastecimento até o combustível de planejamento do manual. A tela e o PDF dizem essa hipótese e a fonte.
- Peso do voo acima do manual: o plano mostra o excesso e não aparece como aceitável, mesmo que a rota exista.
- Catálogo nacional disponível e rota impossível: o plano é gravado como inaceitável, com o motivo, e não inventa um lugar de pouso.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST oferecer como origem, destino e escala os aeródromos de avião da emenda vigente da publicação oficial brasileira de aeródromos. Heliponto MUST NOT entrar.
- **FR-002**: Cada aeródromo MUST guardar identificador publicado, nome, coordenada, elevação e a emenda de onde saiu. Sem essa publicação, o catálogo nacional MUST ficar indisponível e MUST NOT ser completado com valor estimado.
- **FR-003**: O sistema MUST oferecer os modelos de avião pequeno presentes no registro público de aeronaves. Avião pequeno é o de peso máximo de decolagem aprovado igual ou inferior a 5.670 kg. A lista MUST ordenar pelo número de aeronaves do modelo nesse registro, do maior para o menor.
- **FR-004**: Os modelos que, nessa ordem, somam pelo menos 80% das aeronaves de avião pequeno do registro MUST ter o manual oficial gravado. Os demais modelos do registro MUST aparecer, e MUST NOT ser calculados enquanto o manual não estiver gravado.
- **FR-005**: Número de navegação, limite e combustível de planejamento MUST vir do manual oficial do modelo escolhido. Modelo sem manual MUST impedir o cálculo e MUST dizer qual manual falta.
- **FR-006**: O piloto MUST informar origem, destino, hora de partida e os dados particulares do voo. O sistema MUST escolher a rota e as escalas. O piloto MUST NOT precisar indicar a escala.
- **FR-007**: Cada trecho MUST ter combustível para chegar ao pouso do trecho e mais 30 minutos em cruzeiro, como exige o voo visual diurno. O vento só entra na conta quando a fonte oficial de vento cobrir aquele trecho.
- **FR-008**: Entre as rotas em que todos os trechos cumprem o manual, a reserva diurna e o pôr do sol quando ele for conhecido, o sistema MUST escolher a de menor tempo total de voo. Empate de tempo MUST ficar com a rota de menos escalas. Novo empate MUST ficar com a de menor distância.
- **FR-009**: Escala MUST ser um aeródromo de avião da mesma emenda. O plano MUST declarar que, em cada escala, a hipótese é reabastecer até o combustível de planejamento do manual.
- **FR-010**: Se nenhuma rota cumprir a regra, o plano MUST ser mostrado como não aceitável e MUST dizer o limite que impediu. MUST NOT inventar aeródromo, vento, pôr do sol nem número de manual.
- **FR-011**: Cada grandeza da rota, na tela e no PDF, MUST trazer unidade e fonte. O texto MUST explicar o catálogo indisponível, o modelo sem manual e que o resultado não autoriza o voo.
- **FR-012**: O plano continua de um só piloto. Outro piloto MUST NOT ver a rota. O sistema MUST NOT protocolar a rota numa autoridade.

### Key Entities

- **Aeródromo**: Lugar de pouso de avião na emenda vigente, com identificador, nome, coordenada, elevação e fonte da emenda.
- **Modelo de avião**: Avião pequeno do registro público, com a contagem de frota e, quando existir, o manual oficial usado no cálculo.
- **Trecho**: Uma perna entre dois aeródromos, com distância, proa, tempo, combustível, unidade e fonte.
- **Rota**: Sequência ordenada de trechos da origem ao destino, com as escalas escolhidas e o motivo da escolha.
- **Plano**: Continua pertencendo a um piloto e passa a guardar a rota inteira, não só o par origem-destino.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Com a publicação vigente disponível, a lista de origens tem todos os aeródromos de avião dessa emenda e nenhum heliponto.
- **SC-002**: Com o registro de aeronaves disponível, a lista de modelos tem todos os aviões pequenos desse registro, ordenados pela frota. Os modelos que somam pelo menos 80% dessa frota calculam o plano com números do manual. Os outros aparecem e o cálculo recusa, nomeando o manual que falta.
- **SC-003**: Quando o direto cabe na reserva diurna, a rota entregue tem um trecho. Quando não cabe e existe escala possível, cada trecho cabe na reserva e a rota é a de menor tempo total. Quando não existe, o plano fica inaceitável e diz o motivo.
- **SC-004**: Em 100% das grandezas da rota, na tela e no PDF, há unidade e fonte. Em 100% das falhas de publicação, vento, pôr do sol ou manual, o item fica indisponível ou recusado, sem valor inventado.
- **SC-005**: O PDF de uma rota com escala lista os trechos na ordem, a hipótese de reabastecimento e o aviso de que o documento não autoriza o voo.

## Assumptions

- O voo continua visual e diurno. Voo noturno, voo por instrumentos, helicóptero e o envio do plano ao órgão de controle ficam de fora. A rota é apoio ao planejamento, não autorização e não protocolo.
- A publicação oficial de aeródromos é a emenda vigente do ROTAER. O registro oficial de aeronaves é o extrato público do Registro Aeronáutico Brasileiro. A reserva de 30 minutos é a do RBAC nº 91, seção 91.151, para avião em voo visual diurno. O porte de 5.670 kg é o de pequena aeronave no RBAC nº 01.
- "Todas as aeronaves, principalmente as mais usadas" significa todos os modelos de avião pequeno do registro, com manual obrigatório primeiro para o conjunto que soma 80% da frota. Não significa lançar cada matrícula, nem copiar número de um modelo para outro.
- Na escala, a hipótese de planejamento é reabastecer até o combustível de planejamento escrito no manual. O piloto vê essa hipótese. Não é um lançamento de combustível real no pátio.
- O pôr do sol usado é o do aeródromo de chegada do trecho, na data da partida. Se essa hora não vier da fonte, o plano não afirma que o trecho cabe no dia.
- O acesso, o isolamento entre pilotos, o checklist e a impressão já especificados no plano direto continuam valendo. Esta especificação acrescenta o catálogo nacional e a rota com escalas.
- Os sete indicativos e o manual do Cessna 140 já gravados permanecem. Eles não substituem o catálogo nacional.
