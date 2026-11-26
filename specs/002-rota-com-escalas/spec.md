# Feature Specification: Rota com escalas

**Feature Branch**: `002-rota-com-escalas`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Devemos ter todos os aeródromos brasileiros cadastrados. Devemos ter todas as aeronaves de pequeno porte cadastradas, principalmente as mais usadas. O sistema deve otimizar e escolher a melhor rota a partir da origem e do destino e calcular todas as escalas necessárias, com base na documentação oficial e nas melhores práticas de voo."

## Clarifications

### Session 2026-11-25

- Q: Durante uma indisponibilidade da API AISWEB, como a lista local de aeródromos deve funcionar? → A: Consulta e seleção identificadas como locais; bloquear criação e cálculo de plano sem ROTAER vigente.

### Session 2026-11-24

- Q: Para carregar dados técnicos de um modelo, devo tratar AOPA, Pilot-Next e Aeroway apenas como pistas para localizar documentação, aceitando valores no cálculo somente quando conferidos no manual oficial (POH/AFM) da variante exata? → A: Decisão original posteriormente substituída: o usuário autorizou fontes técnicas secundárias rastreáveis para valores usados exclusivamente no produto didático; voo continua visual diurno.
- Q: O combustível usado para testar se um trecho cabe na aeronave deve ser o combustível utilizável indicado na fonte, excluindo a parcela inutilizável, e não a capacidade total dos tanques? → A: Sim. Usar combustível utilizável de fonte aplicável, oficial ou secundária; sem esse dado confiável, não calcular.
- Q: Quando a fonte apresentar várias combinações de velocidade e consumo conforme potência ou altitude, qual deve alimentar o cálculo do trecho? → A: Usar o par nominal de cruzeiro para a mesma condição; se não houver um par nominal identificável, não calcular.
- Q: Para cada conjunto de valores aceito, devo exigir referência suficiente para outra pessoa conferir a fonte e sua aplicabilidade ao modelo? → A: Sim. Para POH/AFM, registrar fabricante, modelo/variante, revisão ou edição e página/tabela; para fonte secundária, registrar publicador, referência, data e modelo/variante declarado.
- Q: Como limitar a seleção de aeronaves no MVP? → A: Oferecer no máximo os 30 primeiros modelos com todos os dados técnicos completos e rastreáveis, oficiais ou secundários, na ordem decrescente de frota; identificar estimativas secundárias como didáticas e manter os demais em espera.
- Q: O que fazer se o extrato RAB vigente estiver indisponível e não for possível garantir a ordem dos 30 primeiros? → A: Deixar a lista indisponível e vazia, sem aceitar modelos locais como substitutos.
- Q: O Cessna 140 deve ter uma regra de elegibilidade especial? → A: Não. Aplicar os mesmos critérios de fonte e completude a todos os modelos, aceitando fonte oficial ou secundária rastreável para uso didático; preservar valores existentes sem usá-los quando a fonte não for verificável.
- Q: Se fontes técnicas rastreáveis divergirem para o mesmo valor, qual deve prevalecer? → A: Priorizar a fonte mais recente, mesmo se menos específica; registrar a divergência e a incerteza, sem calcular média.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Usar qualquer aeródromo brasileiro (Priority: P1)

O piloto escolhe a origem e o destino entre os aeródromos de avião publicados na emenda vigente da lista oficial brasileira. Um heliponto não entra nessa lista. Se a publicação vigente não puder ser consultada, o piloto pode consultar e selecionar a lista local, claramente identificada, mas não criar nem calcular um plano com ela.

**Why this priority**: Sem o catálogo nacional, a rota não pode sair de qualquer aeródromo brasileiro nem pousar numa escala real.

**Independent Test**: Com a publicação vigente disponível, um aeródromo de avião que não estava na semente antiga pode ser origem ou destino. Um heliponto não pode. Sem a publicação, a tela identifica a lista local como não nacional e o servidor recusa qualquer plano com a mensagem de catálogo indisponível.

**Acceptance Scenarios**:

1. **Given** a publicação vigente de aeródromos, **When** o piloto abre a origem, **Then** a lista contém os aeródromos de avião dessa emenda, cada um com o identificador publicado, e não contém heliponto.
2. **Given** um aeródromo de avião dessa emenda que não era um dos sete indicativos antigos, **When** o piloto o usa como origem ou destino, **Then** o plano aceita o lugar e mostra a fonte da coordenada.
3. **Given** a publicação vigente indisponível, **When** o piloto abre a tela de novo plano, **Then** a lista local pode ser consultada e selecionada com identificação explícita de que não é o catálogo nacional; **When** envia o formulário, **Then** o servidor recusa a criação do plano e informa que o catálogo nacional está indisponível.

---

### User Story 2 - Escolher um avião pequeno com dados completos (Priority: P1)

O piloto escolhe entre no máximo 30 modelos de avião pequeno com informação técnica completa e rastreável, oficial ou secundária, priorizados pela frota no Registro Aeronáutico Brasileiro. Modelos incompletos e modelos completos além desse limite ficam em espera e não aparecem na caixa de seleção. Valores secundários são estimativas didáticas; peso, velocidade e consumo não são inventados.

**Why this priority**: A escala depende de dados técnicos rastreáveis e aplicáveis. Sem fonte confiável, não há rota honesta.

**Independent Test**: A caixa de seleção mostra até 30 modelos completos, na ordem de frota. Um modelo incompleto ou além do limite não aparece nem pode ser usado por envio direto. Um avião acima do limite de avião pequeno não entra no catálogo.

**Acceptance Scenarios**:

1. **Given** o registro público de aeronaves e modelos com dados completos, **When** o piloto abre a lista, **Then** vê no máximo os 30 primeiros modelos completos na ordem decrescente de frota.
2. **Given** menos de 30 modelos completos, **When** o piloto abre a lista, **Then** vê todos os modelos completos e nenhum modelo incompleto.
3. **Given** um modelo incompleto ou completo além dos 30 oferecidos, **When** o piloto tenta selecioná-lo ou envia seu identificador diretamente, **Then** o modelo não aparece na caixa e o servidor recusa o plano.
4. **Given** um modelo completo oferecido, **When** o piloto conclui o plano, **Then** navegação, combustível utilizável e limites saem de fonte técnica aplicável, oficial ou secundária, com unidade, publicador, referência e data; os valores secundários aparecem como estimativas didáticas.
5. **Given** que não há extrato RAB vigente, **When** o piloto abre a lista ou envia um plano, **Then** a lista fica indisponível e vazia e o servidor não aceita aeronave local como substituta.

---

### User Story 3 - Receber a melhor rota e as escalas (Priority: P1)

O piloto informa origem, destino e hora. O sistema escolhe a rota. Se o voo direto cabe nos limites dos dados técnicos aplicáveis e na reserva do voo visual diurno, a rota não tem escala. Se não cabe, o sistema inclui só as escalas necessárias, em aeródromos de avião da publicação vigente, e mostra cada trecho. A rota escolhida é a de menor tempo de voo. Se duas rotas levam o mesmo tempo, fica a de menos escalas. Se o empate continuar, fica a mais curta. Se nenhuma rota cumprir a regra, o plano mostra o motivo e não aparece como aceitável.

**Why this priority**: É o pedido central: não deixar o piloto refazer a conta da escala.

**Independent Test**: Num par em que o direto ultrapassa o combustível de planejamento mais a reserva de 30 minutos, o plano volta com pelo menos uma escala e cada trecho dentro da regra, ou volta inaceitável dizendo por que não há rota. Nenhuma escala fica fora do catálogo.

**Acceptance Scenarios**:

1. **Given** origem, destino e um avião cujos dados técnicos aplicáveis permitem o direto com a reserva diurna, **When** o piloto pede o plano, **Then** a rota tem um trecho só, da origem ao destino, com tempo, combustível, unidade e fonte.
2. **Given** um direto que não cabe no combustível de planejamento mais a reserva de 30 minutos, **When** o piloto pede o plano, **Then** a rota inclui as escalas necessárias, cada trecho cumpre a mesma regra, e a rota é a de menor tempo total.
3. **Given** nenhuma sequência de aeródromos publicados deixa todos os trechos dentro da regra, **When** o piloto pede o plano, **Then** o plano não aparece como aceitável e diz qual limite impediu a rota.

---

### User Story 4 - Ler a rota na tela e no PDF (Priority: P2)

Na tela e no PDF o piloto vê cada trecho, a hipótese de reabastecer em cada escala até o combustível de planejamento da fonte aplicável, o que ficou indisponível e o aviso de que o resultado não autoriza o voo. Valores secundários são identificados como estimativas didáticas. O mapa desenha os trechos já calculados. Não há conta de navegação no navegador.

**Why this priority**: A rota só é útil se o piloto conseguir conferir trecho a trecho e imprimir.

**Independent Test**: O PDF de um plano com escala contém origem, cada escala, destino, horário, combustível de cada trecho, a hipótese de reabastecimento e o aviso de que não é autorização.

**Acceptance Scenarios**:

1. **Given** um plano com escala, **When** o piloto abre a tela, **Then** vê a ordem dos trechos, o combustível de cada um e a fonte de cada grandeza.
2. **Given** o mesmo plano, **When** o piloto pede o PDF, **Then** o documento repete os trechos, a hipótese de reabastecimento, as fontes e os rótulos de estimativa didática, quando aplicável, e o aviso de que não substitui o manual, o treinamento nem a norma, e não autoriza o voo.

---

### Edge Cases

- Origem e destino iguais: o plano não é calculado e diz que os lugares precisam ser diferentes.
- Identificador ausente da emenda vigente, ou lugar publicado só como heliponto: o plano não usa esse lugar e diz que não é aeródromo de avião na publicação vigente.
- Publicação de aeródromos indisponível: a tela pode mostrar a lista local identificada como tal para consulta e seleção, mas nada é calculado e nenhum indicativo local é tratado como integrante da lista nacional vigente.
- Extrato RAB vigente indisponível: a lista de modelos fica indisponível e vazia; nenhum modelo local é aceito em plano novo.
- Modelo incompleto, modelo completo além do limite de 30 ou aeronave que não é avião pequeno: o modelo não aparece na seleção; envio direto é recusado.
- Valores de fontes aplicáveis divergentes: priorizar a fonte mais recente, registrar divergência e incerteza e não fazer média; sem data ou aplicabilidade verificável, manter o campo indisponível.
- Vento oficial ausente no trecho: o trecho não ganha componente de vento. O item vento fica indisponível. A rota não assume vento de cauda.
- Hora de nascer ou pôr do sol indisponível: o plano não afirma que o voo cabe no dia. O item fica indisponível.
- Um trecho chegaria depois do pôr do sol no aeródromo de chegada desse trecho: esse trecho não entra numa rota aceitável de voo visual diurno.
- Em cada escala o plano assume reabastecimento até o combustível de planejamento da fonte técnica aplicável. A tela e o PDF dizem essa hipótese e a fonte.
- Peso do voo acima do limite da fonte técnica selecionada: o plano mostra o excesso e não aparece como aceitável, mesmo que a rota exista.
- Catálogo nacional disponível e rota impossível: o plano é gravado como inaceitável, com o motivo, e não inventa um lugar de pouso.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Para aceitar um plano, o sistema MUST exigir que origem, destino e escala pertençam à emenda vigente da publicação oficial brasileira; heliponto MUST NOT entrar. Sem emenda vigente, a tela MAY mostrar a lista local para consulta e seleção, MUST identificá-la como local e incompleta, e o servidor MUST recusar a criação ou o cálculo de plano.
- **FR-002**: Cada aeródromo MUST guardar identificador publicado, nome, coordenada, elevação e a emenda de onde saiu. Sem essa publicação, o catálogo nacional MUST ficar indisponível e MUST NOT ser completado com valor estimado.
- **FR-003**: O sistema MUST manter os modelos de avião pequeno presentes no registro público de aeronaves. Avião pequeno é o de peso máximo de decolagem aprovado igual ou inferior a 5.670 kg. A ordem MUST ser pelo número de aeronaves do modelo nesse registro, do maior para o menor.
- **FR-004**: A caixa de seleção MUST oferecer no máximo os 30 primeiros modelos, nessa ordem de frota, que tenham todos os dados técnicos completos e rastreáveis para o cálculo, oficiais ou secundários. Modelos incompletos e modelos completos além do limite MUST permanecer em espera e MUST NOT aparecer na caixa de seleção nem ser aceitos em `POST` ou `PUT` de plano. Sem extrato RAB vigente, a lista MUST ficar indisponível e vazia, e o servidor MUST NOT aceitar modelos locais como substitutos.
- **FR-005**: Dados técnicos MUST vir de fonte rastreável aplicável ao modelo; fonte oficial não é obrigatória para valores usados exclusivamente no produto didático. Cada valor MUST ter unidade, publicador, referência e data, além do modelo ou variante a que a fonte declara aplicabilidade. Quando for usado POH/AFM, registrar também fabricante, variante, revisão ou edição e página ou tabela. Velocidade e consumo MUST formar o par nominal de cruzeiro para o mesmo perfil. Quando fontes aplicáveis divergirem, MUST prevalecer a mais recente, mesmo que menos específica; registrar divergência e incerteza, sem calcular média. Sem data ou aplicabilidade verificável, o campo MUST ficar indisponível. Todo valor secundário MUST ser identificado como estimativa didática na seleção, resultado e PDF e MUST NOT ser apresentado como adequado a voo real.
- **FR-006**: O piloto MUST informar origem, destino, hora de partida e os dados particulares do voo. O sistema MUST escolher a rota e as escalas. O piloto MUST NOT precisar indicar a escala.
- **FR-007**: Cada trecho MUST ter combustível para chegar ao pouso do trecho e mais 30 minutos em cruzeiro, como exige o voo visual diurno. O vento só entra na conta quando a fonte oficial de vento cobrir aquele trecho.
- **FR-008**: Entre as rotas em que todos os trechos cumprem os dados técnicos aplicáveis, a reserva diurna e o pôr do sol quando ele for conhecido, o sistema MUST escolher a de menor tempo total de voo. Empate de tempo MUST ficar com a rota de menos escalas. Novo empate MUST ficar com a de menor distância.
- **FR-009**: Escala MUST ser um aeródromo de avião da mesma emenda. O plano MUST declarar que, em cada escala, a hipótese é reabastecer até o combustível de planejamento indicado pela fonte técnica aplicável.
- **FR-010**: Se nenhuma rota cumprir a regra, o plano MUST ser mostrado como não aceitável e MUST dizer o limite que impediu. MUST NOT inventar aeródromo, vento, pôr do sol nem dado técnico de aeronave.
- **FR-011**: Cada grandeza da rota, na tela e no PDF, MUST trazer unidade e fonte. Valores secundários MUST também identificar publicador, referência, data e aplicabilidade e aparecer como estimativa didática. O texto MUST explicar o catálogo indisponível, a indisponibilidade de modelo fora do limite do MVP e que o resultado não autoriza nem é adequado para voo real.
- **FR-012**: O plano continua de um só piloto. Outro piloto MUST NOT ver a rota. O sistema MUST NOT protocolar a rota numa autoridade.

### Key Entities

- **Aeródromo**: Lugar de pouso de avião na emenda vigente, com identificador, nome, coordenada, elevação e fonte da emenda.
- **Modelo de avião**: Avião pequeno do registro público, com a contagem de frota e a fonte técnica oficial ou secundária usada no cálculo.
- **Trecho**: Uma perna entre dois aeródromos, com distância, proa, tempo, combustível, unidade e fonte.
- **Rota**: Sequência ordenada de trechos da origem ao destino, com as escalas escolhidas e o motivo da escolha.
- **Plano**: Continua pertencendo a um piloto e passa a guardar a rota inteira, não só o par origem-destino.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Com a publicação vigente disponível, a lista de origens tem todos os aeródromos de avião dessa emenda e nenhum heliponto.
- **SC-006**: Sem emenda vigente, a tela identifica a lista local como não nacional e permite consultá-la, mas 100% das tentativas de criar ou calcular um plano são recusadas com o motivo de catálogo nacional indisponível.
- **SC-002**: Com o registro de aeronaves disponível, a caixa de seleção contém de zero a 30 modelos completos com fontes técnicas rastreáveis, na ordem decrescente de frota. Nenhum modelo incompleto ou além do limite aparece ou pode ser usado por envio direto. Sem registro vigente, a lista fica indisponível e vazia e nenhum modelo é aceito em plano novo.
- **SC-003**: Quando o direto cabe na reserva diurna, a rota entregue tem um trecho. Quando não cabe e existe escala possível, cada trecho cabe na reserva e a rota é a de menor tempo total. Quando não existe, o plano fica inaceitável e diz o motivo.
- **SC-004**: Em 100% das grandezas da rota, na tela e no PDF, há unidade e fonte; todo valor secundário também identifica publicador, referência, data, aplicabilidade e o rótulo de estimativa didática. Em 100% das falhas de publicação, vento, pôr do sol ou fonte técnica, o item fica indisponível ou recusado, sem valor inventado.
- **SC-005**: O PDF de uma rota com escala lista os trechos na ordem, a hipótese de reabastecimento e o aviso de que o documento não autoriza o voo.

## Assumptions

- O voo continua visual e diurno. Voo noturno, voo por instrumentos, helicóptero e o envio do plano ao órgão de controle ficam de fora. A rota é apoio ao planejamento, não autorização e não protocolo.
- A publicação oficial de aeródromos é a emenda vigente do ROTAER. O registro oficial de aeronaves é o extrato público do Registro Aeronáutico Brasileiro. A reserva de 30 minutos é a do RBAC nº 91, seção 91.151, para avião em voo visual diurno. O porte de 5.670 kg é o de pequena aeronave no RBAC nº 01.
- O MVP mantém os modelos do registro, mas oferece apenas os 30 primeiros com informação técnica completa e rastreável na ordem de frota. Fontes secundárias são permitidas exclusivamente para fins didáticos; os demais modelos ficam em espera, sem aparecer na seleção. Não significa lançar cada matrícula, nem copiar número de um modelo para outro.
- Na escala, a hipótese de planejamento é reabastecer até o combustível de planejamento escrito na fonte técnica aplicável. O piloto vê essa hipótese. Não é um lançamento de combustível real no pátio.
- O pôr do sol usado é o do aeródromo de chegada do trecho, na data da partida. Se essa hora não vier da fonte, o plano não afirma que o trecho cabe no dia.
- O acesso, o isolamento entre pilotos, o checklist e a impressão já especificados no plano direto continuam valendo. Esta especificação acrescenta o catálogo nacional e a rota com escalas.
- Os sete indicativos antigos e os registros técnicos já existentes permanecem armazenados, mas não substituem o catálogo nacional. Todos os modelos, inclusive os já semeados, passam pelos mesmos critérios de elegibilidade; valores sem fonte técnica rastreável e aplicável não são usados.
- A lista local de aeródromos pode permanecer visível como recurso de consulta e seleção quando a API estiver indisponível, mas nunca valida origem, destino ou escala para um plano sem emenda ROTAER vigente.

## Review

A validação de requisitos de negócio e os testes funcionais são a sexta porta futura da suíte de revisão, registrada em `specs/revisao-codigo-pronto/tasks.md`. Esta menção não executa essa porta.
