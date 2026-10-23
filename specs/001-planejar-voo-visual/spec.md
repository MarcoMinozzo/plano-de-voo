# Feature Specification: Planejar voo visual

**Feature Branch**: `001-planejar-voo-visual`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "O piloto informa origem, destino e hora de partida. Dados técnicos vêm dos manuais; dados particulares deste voo são informados pelo piloto. Meteorologia relevante vem de fontes atualizadas. O sistema é para aviões de pequeno porte em voo visual. Calcula navegação, manutenção aplicável ao voo, combustível e o plano segundo as normas vigentes. Fornece cartas de voo atualizadas e mapa de radar de chuva. Calcula e mostra o perfil de vento. Sugere checklist. Permite imprimir o plano em PDF. O piloto entra com senha, sem segundo fator, num espaço só dele. Vê os planos anteriores, e pode editar ou apagar."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Montar e calcular o plano (Priority: P1)

Um piloto de avião pequeno, já identificado no seu espaço, informa de onde sai, para onde vai e a que horas precisa partir. O sistema busca no manual oficial da aeronave escolhida os dados técnicos do voo e pede ao piloto só o que é particular deste voo. Em seguida calcula a navegação, o combustível necessário e o plano de voo visual segundo as normas vigentes, com unidade e origem de cada número.

**Why this priority**: Sem este cálculo não existe plano de voo. Os mapas, o checklist e a impressão dependem dele.

**Independent Test**: Com um piloto identificado e uma aeronave cujo manual está disponível, informar origem, destino e hora e receber navegação, combustível e plano, cada número com unidade e fonte.

**Acceptance Scenarios**:

1. **Given** um piloto no seu espaço e uma aeronave com manual disponível, **When** informa origem, destino e hora de partida e os dados particulares do voo, **Then** o sistema mostra o plano visual com navegação, combustível e limites aplicáveis do manual, cada grandeza com unidade e com a fonte (manual ou norma).
2. **Given** o piloto escolhe uma aeronave sem manual disponível, **When** tenta concluir o plano, **Then** o sistema recusa o cálculo e diz qual manual falta. Não pede ao piloto para inventar o dado técnico.
3. **Given** um peso, um combustível ou outro limite do manual é ultrapassado, **When** o plano é calculado, **Then** o piloto vê qual limite foi ultrapassado e o plano não aparece como aceitável.

---

### User Story 2 - Entrar no espaço próprio (Priority: P1)

O piloto cria o acesso com identificação e senha, sem segundo fator, entra e passa a ver só os próprios planos. Outro piloto não vê, não edita e não apaga esse conteúdo.

**Why this priority**: O painel e o histórico são do piloto. Sem o espaço separado, um plano se mistura com o de outra pessoa.

**Independent Test**: Dois pilotos entram em acessos diferentes. O plano criado por um não aparece para o outro.

**Acceptance Scenarios**:

1. **Given** um piloto sem acesso, **When** cria identificação e senha e entra, **Then** vê o próprio painel, vazio se ainda não houver plano.
2. **Given** dois pilotos com acessos diferentes, **When** o primeiro grava um plano, **Then** o segundo não vê esse plano no painel, nem consegue abri-lo, editá-lo ou apagá-lo.
3. **Given** um piloto já cadastrado, **When** informa a senha errada, **Then** o acesso é recusado, nenhum plano é mostrado, e a mensagem é a mesma de uma identificação que não existe.
4. **Given** uma identificação com cinco recusas nos últimos 15 minutos, **When** a senha certa é informada dentro desse bloqueio, **Then** o acesso continua recusado até passar 15 minutos, com a mesma mensagem.
5. **Given** um piloto que saiu, **When** reutiliza a sessão anterior, **Then** nenhum plano abre.

---

### User Story 3 - Ver tempo, carta, radar e vento (Priority: P2)

No plano em montagem, o piloto vê a meteorologia importante para aquele voo, a carta de navegação visual atualizada do trajeto, o radar de chuva da mesma região e o perfil de vento. O vento aparece com direção, velocidade e o efeito no voo, de um jeito que o piloto lê sem refazer a conta.

**Why this priority**: O cálculo do plano precisa do tempo e do vento, e a carta com o radar é o que o piloto usa para o voo visual. O plano ainda tem valor se a carta atrasar, desde que a falha fique visível.

**Independent Test**: Num plano com origem, destino e hora, conferir que tempo, carta, radar e vento aparecem para aquele trajeto, e que a falta de qualquer um deles é mostrada como falta.

**Acceptance Scenarios**:

1. **Given** um plano com origem, destino e hora e fontes disponíveis, **When** o piloto abre o tempo, a carta, o radar e o vento, **Then** vê dados atuais da rota, a carta de voo visual da região e o radar de chuva sobre a mesma área, além do vento com direção, velocidade e efeito no voo.
2. **Given** a meteorologia, o vento, a carta ou o radar não está disponível, **When** o piloto consulta esse item, **Then** vê que está indisponível e nenhum valor é preenchido no lugar.

---

### User Story 4 - Checklist e impressão (Priority: P2)

Ao final, o sistema sugere o checklist daquele voo, a partir do manual da aeronave e da preparação do voo visual. O piloto imprime o plano em PDF com rota, horários, combustível, vento, resumo do tempo e checklist.

**Why this priority**: É o fechamento do plano. O piloto só imprime depois que o plano existe.

**Independent Test**: A partir de um plano calculado, marcar o checklist sugerido e obter um PDF que contém as partes do plano e o aviso de que o resultado não autoriza o voo.

**Acceptance Scenarios**:

1. **Given** um plano calculado, **When** o piloto abre o checklist, **Then** vê a lista sugerida para aquela aeronave e aquele voo visual, e pode marcá-la.
2. **Given** um plano calculado, **When** o piloto pede a impressão, **Then** recebe um PDF com rota, horários, combustível, vento, resumo meteorológico, checklist e o aviso de que o documento não substitui o manual, o treinamento nem a norma, e não autoriza o voo.

---

### User Story 5 - Rever planos anteriores (Priority: P2)

No painel, o piloto vê os planos que já fez. Abre um, altera os dados e o plano é recalculado, ou apaga um plano que não quer mais.

**Why this priority**: O histórico só faz sentido depois que existe pelo menos um plano gravado.

**Independent Test**: Gravar dois planos, editar um, apagar o outro e ver o painel refletir as duas ações.

**Acceptance Scenarios**:

1. **Given** um piloto com planos gravados, **When** abre o painel, **Then** vê a lista dos próprios planos, com origem, destino e hora de partida.
2. **Given** um plano anterior do piloto, **When** ele altera origem, destino, hora ou um dado particular e confirma, **Then** o plano é recalculado com o tempo e o vento atuais e a lista mostra a versão nova.
3. **Given** um plano anterior do piloto, **When** ele apaga e confirma, **Then** o plano some do painel e deixa de poder ser aberto.

---

### User Story 6 - Entender o plano na tela (Priority: P2)

Na própria tela do plano, e no PDF, o piloto lê o que precisa informar, o que significa um item indisponível e o aviso de que o resultado não autoriza o voo. Não precisa de outro documento para isso.

**Why this priority**: O aviso e o significado de uma falha fazem parte do plano. Sem eles, um número pode ser lido como autorização.

**Independent Test**: Abrir um plano com o radar indisponível e achar, na mesma tela, a explicação de indisponível e o aviso. O PDF traz os dois.

**Acceptance Scenarios**:

1. **Given** um piloto na tela do plano, **When** procura a orientação, **Then** vê o que informar, o que é um item indisponível e o aviso de que o resultado não substitui o manual, o treinamento nem a norma, e não autoriza o voo.
2. **Given** um plano impresso, **When** o piloto lê o PDF, **Then** encontra a mesma orientação e o mesmo aviso.

---

### User Story 7 - Subir o sistema pela documentação de operação (Priority: P2)

Quem opera o sistema segue um texto do projeto e consegue preparar o banco, colocar as chaves fora do repositório e subir o serviço. O texto não contém senha nem chave.

**Why this priority**: Sem esse texto, a operação depende de quem escreveu o código. Não bloqueia o piloto que já tem o sistema no ar.

**Independent Test**: Uma pessoa que não alterou o código segue só o texto de operação e sobe o sistema numa base vazia, sem achar segredo nesse texto.

**Acceptance Scenarios**:

1. **Given** o texto de operação e uma base vazia, **When** o operador segue os passos, **Then** o sistema sobe e um piloto consegue se cadastrar.
2. **Given** o texto de operação, **When** se procura senha, chave de radar ou chave de carta, **Then** nenhum segredo está escrito. O texto só diz onde esses valores ficam.

---

### Edge Cases

- Origem e destino iguais, ou um aeródromo que o sistema não reconhece: o plano não é calculado e o piloto vê qual campo precisa corrigir.
- Hora de partida no passado: o piloto é avisado e confirma se ainda quer planejar aquele horário.
- Manual da aeronave sem o dado exigido pela conta (combustível utilizável, limite de peso ou velocidade de planejamento): a conta para e diz qual dado do manual falta.
- Meteorologia, vento, carta ou radar indisponível: o item aparece como indisponível. O restante do plano continua visível. Nenhum boletim, vento ou mapa é inventado.
- Limite do manual ultrapassado (peso, bagagem, combustível ou centro de gravidade, quando o manual trouxer esse limite): o plano mostra o excesso e não é apresentado como aceitável.
- Senha com menos de 8 caracteres: o cadastro é recusado e diz a regra, sem criar o acesso.
- Senha errada, identificação inexistente, ou identificação bloqueada por cinco recusas em 15 minutos: a mesma mensagem de recusa, sem dizer qual dos três casos ocorreu, e nenhum plano é mostrado.
- Sessão sem uso por 8 horas, ou piloto que saiu: a sessão não abre planos.
- Tentativa de abrir plano de outro piloto: acesso recusado, sem revelar se o plano existe.
- Apagar plano: só ocorre depois de confirmação. Cancelar a confirmação mantém o plano.
- Editar um plano antigo: tempo, vento, carta e radar são buscados de novo. O que falhar fica marcado como indisponível.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O piloto MUST informar origem, destino e hora de partida para iniciar um plano.
- **FR-002**: O sistema MUST obter os dados técnicos do voo no manual oficial da aeronave escolhida. Dados técnicos incluem os números de navegação, os limites e as verificações de manutenção que o manual manda observar para o voo, e o combustível de planejamento.
- **FR-003**: O piloto MUST informar os dados particulares deste voo. Dados particulares são os que mudam a cada voo e não estão no manual, como ocupantes, pesos deste voo e combustível a bordo.
- **FR-004**: O sistema MUST buscar a meteorologia importante para o voo em fontes aeronáuticas atualizadas. Se a fonte não responder, o piloto MUST ver a falha.
- **FR-005**: O sistema MUST atender avião de pequeno porte em voo visual. Helicóptero, planador, balão e voo por instrumentos ficam de fora.
- **FR-006**: O sistema MUST calcular os dados de voo exigidos pelo manual da aeronave e pela norma de voo visual vigente, incluindo navegação e combustível necessário, e MUST montar o plano de voo de acordo com essa norma.
- **FR-007**: Cada grandeza mostrada ou impressa MUST trazer a unidade e a fonte, manual ou norma.
- **FR-008**: O sistema MUST fornecer a carta de voo do trajeto dentro da prática de navegação visual, com dados atualizados, e o mapa de radar de chuva da mesma região.
- **FR-009**: O sistema MUST calcular o perfil de vento do trajeto e MUST mostrá-lo com direção, velocidade e efeito no voo, de forma que o piloto leia o resultado sem refazer a conta.
- **FR-010**: O sistema MUST sugerir o checklist daquele voo, a partir do manual da aeronave e da preparação do voo visual. O piloto MUST poder marcar os itens.
- **FR-011**: O piloto MUST poder imprimir o plano concluído em PDF.
- **FR-012**: O piloto MUST entrar com identificação e senha, sem segundo fator, para usar um espaço só dele.
- **FR-013**: O piloto MUST ver no painel os próprios planos anteriores.
- **FR-014**: O piloto MUST poder editar um plano anterior. A edição MUST recalcular o plano.
- **FR-015**: O piloto MUST poder apagar um plano anterior, somente após confirmação.
- **FR-016**: Um piloto MUST NOT ver, editar ou apagar plano de outro piloto.
- **FR-017**: O sistema MUST NOT inventar meteorologia, vento, carta ou radar quando a fonte não tiver o dado.
- **FR-018**: O plano na tela e o PDF MUST declarar que o resultado não substitui o manual da aeronave, o treinamento de voo nem a norma vigente, e que não é autorização de voo.
- **FR-019**: A senha MUST ter no mínimo 8 caracteres. Senha menor MUST ser recusada no cadastro.
- **FR-020**: A mensagem de entrada recusada MUST ser a mesma quando a identificação não existe, quando a senha está errada e quando a identificação está bloqueada.
- **FR-021**: Cinco recusas em 15 minutos para a mesma identificação MUST impedir novas tentativas por 15 minutos.
- **FR-022**: A sessão MUST encerrar quando o piloto sai e quando ficam 8 horas sem uso. A sessão encerrada MUST NOT abrir planos.
- **FR-023**: A tela do plano e o PDF MUST explicar o que o piloto informa e o que significa um item indisponível, junto com o aviso de FR-018.
- **FR-024**: O projeto MUST ter um texto de operação que permita preparar o banco, indicar onde ficam as chaves e subir o serviço. Esse texto MUST NOT conter senha nem chave.

### Key Entities

- **Piloto**: pessoa que entra no espaço próprio e guarda os seus planos. Identificação e senha de no mínimo 8 caracteres. Pode ficar temporariamente bloqueado depois de recusas seguidas. Não compartilha o espaço com outro piloto nesta versão.
- **Orientação do piloto**: texto na tela e no PDF sobre o que informar, o que é indisponível e o aviso de que o plano não autoriza o voo.
- **Texto de operação**: instruções para preparar o banco, guardar chaves fora do projeto e subir o serviço, sem segredos escritos.
- **Aeronave**: avião de pequeno porte escolhido para o voo, ligado ao manual oficial de onde saem os dados técnicos.
- **Plano de voo**: o voo visual planejado. Liga piloto, aeronave, origem, destino, hora de partida, dados particulares, cálculos, tempo, vento, carta, radar, checklist e o documento impresso.
- **Dado particular do voo**: valor deste voo informado pelo piloto, distinto do número fixo do manual.
- **Condição meteorológica**: informação atual de tempo relevante ao trajeto e à hora, com a indicação de indisponível quando faltar.
- **Perfil de vento**: vento ao longo do trajeto, com direção, velocidade e efeito no voo.
- **Checklist sugerido**: lista de verificação proposta para aquele voo, que o piloto marca.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um piloto que já entrou no seu espaço, com o manual da aeronave disponível e com tempo e vento disponíveis, conclui um plano de voo visual, da origem ao PDF, em até 15 minutos.
- **SC-002**: 100% das grandezas do plano e do PDF mostram unidade e fonte.
- **SC-003**: Em 100% dos casos em que tempo, vento, carta ou radar faltam, o piloto vê o item como indisponível e nenhum valor inventado entra no plano.
- **SC-004**: Em uma verificação com dois pilotos, nenhum consegue abrir, editar ou apagar o plano do outro.
- **SC-005**: Depois de editar ou apagar um plano, o painel mostra a lista atualizada na mesma visita, sem o plano apagado e com a versão nova do plano editado.
- **SC-006**: O PDF contém rota, horários, combustível, vento, resumo do tempo, checklist, a explicação de item indisponível e o aviso de que o documento não autoriza o voo.
- **SC-007**: Senha com menos de 8 caracteres não cria acesso. Na sexta tentativa dentro de 15 minutos depois de cinco recusas, a entrada continua recusada mesmo com a senha certa, e a mensagem é igual à de uma identificação inexistente.
- **SC-008**: Quem segue só o texto de operação sobe o sistema numa base vazia. Esse texto não contém senha nem chave.

## Assumptions

O catálogo nacional de aeródromos, o catálogo de aviões pequenos e a rota com escalas estão em `specs/002-rota-com-escalas/`. Este documento descreve o plano direto já especificado, com a semente de sete aeródromos e o manual do Cessna 140.

- O voo é visual, de avião pequeno, no Brasil, e a norma vigente é a de voo visual aplicável a esse caso. Voo noturno, voo por instrumentos e envio do plano ao órgão de controle ficam fora desta versão. O sistema prepara e imprime o plano; não protocola o plano numa autoridade.
- A interface e o PDF ficam em português.
- O piloto escolhe uma aeronave cujo manual oficial o sistema já possui. O primeiro manual disponível é o do Cessna 140. Outro avião pequeno de voo visual entra quando o manual correspondente estiver disponível. O piloto não digita o número técnico que o manual já traz.
- "Manutenção do avião" aqui são as verificações e os limites que o manual manda observar para liberar o voo, não um diário de manutenção nem uma oficina.
- A carta é a carta de navegação visual atualizada da região do trajeto. O radar é o radar de precipitação atual da mesma região.
- O perfil de vento usa o vento nas altitudes de planejamento ao longo da rota.
- O acesso desta versão é identificação e senha, sem segundo fator. A senha tem no mínimo 8 caracteres. Cinco recusas em 15 minutos bloqueiam a identificação por 15 minutos. A sessão cai ao sair e após 8 horas sem uso. Recuperação de senha e acesso compartilhado ficam fora.
- Um plano gravado guarda a origem, o destino, a hora, a aeronave, os dados particulares e o resultado. Ao editar, tempo, vento, carta e radar são consultados de novo.
- O resultado continua sendo apoio ao planejamento. Não substitui o manual, o treinamento nem a norma, e não autoriza o voo.
