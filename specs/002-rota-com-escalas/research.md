# Research: Rota com escalas

## Catálogo de aeródromos

- **Decision**: A lista nacional vem da área `rotaer` da API AISWEB, emenda vigente. Entra o registro cujo tipo publicado é aeródromo. Heliponto fica de fora. Cada registro guarda o identificador publicado, o nome, a coordenada, a elevação e o identificador da emenda. Sem chave, sem resposta ou sem emenda reconhecível, o catálogo nacional fica `indisponivel`.
- **Rationale**: O AISWEB é a fonte oficial de informação aeronáutica do Brasil, e o ROTAER é o produto que descreve os aeródromos. A constituição 4.0.0 proíbe coordenada estimada e proíbe tratar os sete indicativos antigos como o país inteiro.
- **Alternatives considered**: Manter só SBJD, SBAU, SBBU, SBML, SBDN, SBKP e SBRP não atende "todos os aeródromos brasileiros". Copiar uma lista solta para o repositório ficaria velha na emenda seguinte.

## Catálogo de aviões

- **Decision**: Os modelos vêm do extrato público do Registro Aeronáutico Brasileiro. Entra modelo de avião com peso máximo de decolagem aprovado igual ou inferior a 5.670 kg, que é a pequena aeronave do RBAC nº 01. A ordem é a quantidade de aeronaves do modelo, da maior frota para a menor. O MVP oferece no máximo os primeiros 30 modelos completos nessa ordem; os demais permanecem em espera e não são oferecidos.
- **Rationale**: O limite mantém o MVP concentrado nos modelos mais usados que tenham documentação suficiente. Inventar peso ou consumo de um modelo quebraria a constituição.
- **Alternatives considered**: Cadastrar cada matrícula duplicaria o mesmo manual milhares de vezes. Uma lista fixa de nomes de modelo, sem o extrato, não se atualiza e não prova o que é "mais usada".

## Dados técnicos de aeronaves

- **Decision**: POH/AFM oficial ou fonte técnica secundária rastreável pode fornecer os valores usados exclusivamente no produto didático. Fontes indicadas para pesquisa inicial: AOPA Aircraft Fact Sheets, Pilot-Next e Aeroway; FAA continua sendo uma fonte regulatória oficial. A lista é ponto de partida, não comprovação de cobertura de variante.
- **Rationale**: O usuário autorizou fontes secundárias porque o software é puramente didático para desenvolvimento de software. A constituição 4.0.0 exige que esses valores sejam identificados como estimativas e não como dados adequados a voo real.
- **Decision**: Cada valor tem procedência própria: campo, valor e unidade; publicador, referência, data de publicação e consulta, modelo/variante e perfil quando aplicável. Fontes usadas para um cálculo devem ter aplicabilidade declarada; valores sem data ou aplicabilidade verificável ficam indisponíveis. Para POH/AFM, registrar também fabricante, edição/revisão e página/tabela.
- **Rationale**: Um único texto de `fonte_manual` não permite auditar campos obtidos de publicadores diferentes nem explicar conflito de valores.
- **Decision**: Em fontes aplicáveis divergentes, escolher a publicação mais recente mesmo se menos específica; registrar os valores conflitantes e a incerteza, sem média. Velocidade e consumo continuam pareados no mesmo perfil nominal; combustível deve ser utilizável, não a capacidade total.
- **Rationale**: A regra segue a decisão explícita do usuário e impede mistura silenciosa de perfis incompatíveis.
- **Decision**: Manter os valores técnicos existentes em `Aeronave` para os cálculos e adicionar registros estruturados de proveniência por campo/fonte. `manual_estado="gravado"` passa a significar que os campos obrigatórios e suas fontes foram conferidos, sem indicar certificação ou validade operacional.
- **Rationale**: O esquema atual possui um único `fonte_manual` para vários valores. Registros por campo permitem que o catálogo, a resposta da API, a tela e o PDF exibam a fonte correspondente a cada grandeza.
- **Alternatives considered**: Um texto livre único em `fonte_manual` não vincula fontes a cada valor. Atualização manual direta do banco não deixa uma carga reproduzível.
- **Decision**: Os registros de proveniência e valores revisados entram por uma carga reproduzível em `servidor/semente.py`; a conferência humana confirma unidade, publicador, data, referência, aplicabilidade e perfil antes de marcar completude. O RAB continua determinando frota e ordem.
- **Rationale**: Reutiliza o caminho de carga existente e mantém o banco relacional como armazenamento de runtime.
- **Open execution input**: Nenhum valor de fonte secundária foi validado nem importado nesta etapa. As fontes sugeridas ainda precisam ser pesquisadas por modelo/variante. A lista de frota continua condicionada ao extrato RAB e à unidade confirmada do PMD.
- **Decision**: Se não houver extrato RAB vigente, `GET /aeronaves` retorna indisponível e sem modelos, e o servidor não aceita plano novo com aeronave local. Sem o extrato não há ranking atual que prove quais modelos pertencem às 30 posições.
- **Rationale**: Manter modelos locais selecionáveis nessa situação enfraqueceria a regra de apresentar somente os primeiros modelos completos em ordem de frota.
- **Open execution input**: Não há extrato RAB vigente nem POH/AFM verificáveis dos 30 modelos no repositório. A ordem depende do arquivo indicado por `RAB_EXTRATO`; os valores só podem ser preenchidos após consulta dos POH/AFM aplicáveis. Registros existentes com fonte “números de estudo” não são oficiais e devem ser avaliados pela mesma regra de todos os modelos; preservar os valores não os torna elegíveis.

## Reserva e escala

- **Decision**: Cada trecho precisa de combustível para o pouso do trecho mais 30 minutos em cruzeiro. A fonte é o RBAC nº 91, seção 91.151, avião em voo visual diurno. O vento oficial só altera o trecho quando o produto de área da REDEMET cobre esse trecho. Sem vento, não há crédito de cauda. Em cada escala a hipótese é reabastecer até o combustível de planejamento indicado pela fonte técnica selecionada, e o plano mostra essa frase com a fonte.
- **Rationale**: A norma manda considerar vento e meteorologia conhecidos. Vento desconhecido não vira vento favorável. A escala é pouso para cumprir o trecho seguinte, não um ponto inventado no mapa.
- **Alternatives considered**: Usar a reserva noturna de 45 minutos alargaria o produto para voo noturno, que esta versão exclui. Deixar o piloto escolher a escala à mão não responde o pedido de o sistema escolher.

## Qual rota é a melhor

- **Decision**: Entre as rotas em que todo trecho cumpre os dados técnicos selecionados, reserva diurna e, quando conhecido, o pôr do sol do aeródromo de chegada, fica a de menor tempo total. Empate de tempo fica com menos escalas. Novo empate fica com menor distância. O direto ganha quando ele mesmo cumpre a regra. A busca no servidor só liga dois aeródromos se a distância ainda em ar calmo couber no combustível de planejamento menos a reserva. O pôr do sol vem da área `sol` do AISWEB. Sem essa hora, o item fica indisponível e a rota não é apresentada como cabendo no dia.
- **Rationale**: Menor tempo é o que o piloto lê como melhor rota sem refazer a conta. Menos escalas e menor distância só desempatam. Limitar a aresta ao alcance evita varrer pares impossíveis e mantém a conta no servidor.
- **Alternatives considered**: Uma nota combinando paisagem, espaço aéreo e preferência do piloto não está na documentação oficial usada aqui. Carta de corredor visual não substitui a conta de combustível. Protocolar a rota no órgão de controle continua fora.

## O que não muda

- **Decision**: Sessão, isolamento, checklist, carta WAC, radar e PDF continuam como no plano direto. O mapa Leaflet só recebe a lista de pontos já calculada.
- **Rationale**: Esta feature acrescenta catálogo e rota. Não reabre o acesso nem move fórmula para o JavaScript.
- **Alternatives considered**: Um serviço separado de roteamento aumentaria a pilha sem necessidade.
