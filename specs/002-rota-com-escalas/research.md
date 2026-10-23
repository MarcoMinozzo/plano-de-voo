# Research: Rota com escalas

## Catálogo de aeródromos

- **Decision**: A lista nacional vem da área `rotaer` da API AISWEB, emenda vigente. Entra o registro cujo tipo publicado é aeródromo. Heliponto fica de fora. Cada registro guarda o identificador publicado, o nome, a coordenada, a elevação e o identificador da emenda. Sem chave, sem resposta ou sem emenda reconhecível, o catálogo nacional fica `indisponivel`.
- **Rationale**: O AISWEB é a fonte oficial de informação aeronáutica do Brasil, e o ROTAER é o produto que descreve os aeródromos. A constituição 2.2.0 proíbe coordenada estimada e proíbe tratar os sete indicativos antigos como o país inteiro.
- **Alternatives considered**: Manter só SBJD, SBAU, SBBU, SBML, SBDN, SBKP e SBRP não atende "todos os aeródromos brasileiros". Copiar uma lista solta para o repositório ficaria velha na emenda seguinte.

## Catálogo de aviões

- **Decision**: Os modelos vêm do extrato público do Registro Aeronáutico Brasileiro. Entra modelo de avião com peso máximo de decolagem aprovado igual ou inferior a 5.670 kg, que é a pequena aeronave do RBAC nº 01. A ordem é a quantidade de aeronaves do modelo, da maior frota para a menor. Os modelos que somam 80% dessa frota precisam ter o manual oficial gravado, com cada número e a citação do manual. Modelo sem manual fica visível e não calcula.
- **Rationale**: "Todas, principalmente as mais usadas" cobre o registro inteiro e exige manual primeiro onde está a maior parte da frota. Inventar peso ou consumo de um modelo quebraria a constituição.
- **Alternatives considered**: Cadastrar cada matrícula duplicaria o mesmo manual milhares de vezes. Uma lista fixa de nomes de modelo, sem o extrato, não se atualiza e não prova o que é "mais usada".

## Reserva e escala

- **Decision**: Cada trecho precisa de combustível para o pouso do trecho mais 30 minutos em cruzeiro. A fonte é o RBAC nº 91, seção 91.151, avião em voo visual diurno. O vento oficial só altera o trecho quando o produto de área da REDEMET cobre esse trecho. Sem vento, não há crédito de cauda. Em cada escala a hipótese é reabastecer até o combustível de planejamento do manual, e o plano mostra essa frase com a fonte do manual.
- **Rationale**: A norma manda considerar vento e meteorologia conhecidos. Vento desconhecido não vira vento favorável. A escala é pouso para cumprir o trecho seguinte, não um ponto inventado no mapa.
- **Alternatives considered**: Usar a reserva noturna de 45 minutos alargaria o produto para voo noturno, que esta versão exclui. Deixar o piloto escolher a escala à mão não responde o pedido de o sistema escolher.

## Qual rota é a melhor

- **Decision**: Entre as rotas em que todo trecho cumpre manual, reserva diurna e, quando conhecido, o pôr do sol do aeródromo de chegada, fica a de menor tempo total. Empate de tempo fica com menos escalas. Novo empate fica com menor distância. O direto ganha quando ele mesmo cumpre a regra. A busca no servidor só liga dois aeródromos se a distância ainda em ar calmo couber no combustível de planejamento menos a reserva. O pôr do sol vem da área `sol` do AISWEB. Sem essa hora, o item fica indisponível e a rota não é apresentada como cabendo no dia.
- **Rationale**: Menor tempo é o que o piloto lê como melhor rota sem refazer a conta. Menos escalas e menor distância só desempatam. Limitar a aresta ao alcance evita varrer pares impossíveis e mantém a conta no servidor.
- **Alternatives considered**: Uma nota combinando paisagem, espaço aéreo e preferência do piloto não está na documentação oficial usada aqui. Carta de corredor visual não substitui a conta de combustível. Protocolar a rota no órgão de controle continua fora.

## O que não muda

- **Decision**: Sessão, isolamento, checklist, carta WAC, radar e PDF continuam como no plano direto. O mapa Leaflet só recebe a lista de pontos já calculada.
- **Rationale**: Esta feature acrescenta catálogo e rota. Não reabre o acesso nem move fórmula para o JavaScript.
- **Alternatives considered**: Um serviço separado de roteamento aumentaria a pilha sem necessidade.
