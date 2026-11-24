# Research: Rota com escalas

## Catálogo de aeródromos

- **Decision**: A lista nacional vem da área `rotaer` da API AISWEB, emenda vigente. Entra o registro cujo tipo publicado é aeródromo. Heliponto fica de fora. Cada registro guarda o identificador publicado, o nome, a coordenada, a elevação e o identificador da emenda. Sem chave, sem resposta ou sem emenda reconhecível, o catálogo nacional fica `indisponivel`.
- **Rationale**: O AISWEB é a fonte oficial de informação aeronáutica do Brasil, e o ROTAER é o produto que descreve os aeródromos. A constituição 2.2.0 proíbe coordenada estimada e proíbe tratar os sete indicativos antigos como o país inteiro.
- **Alternatives considered**: Manter só SBJD, SBAU, SBBU, SBML, SBDN, SBKP e SBRP não atende "todos os aeródromos brasileiros". Copiar uma lista solta para o repositório ficaria velha na emenda seguinte.

## Catálogo de aviões

- **Decision**: Os modelos vêm do extrato público do Registro Aeronáutico Brasileiro. Entra modelo de avião com peso máximo de decolagem aprovado igual ou inferior a 5.670 kg, que é a pequena aeronave do RBAC nº 01. A ordem é a quantidade de aeronaves do modelo, da maior frota para a menor. Os 20 primeiros modelos não experimentais dessa ordem precisam ter o manual oficial gravado, com cada número e a citação do manual (clarificação de 2026-11-24; a meta de 80% fica para revisão). Modelo sem manual fica visível e não calcula.
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

## Registro dos manuais (revisão de 2026-11-24)

- **Decision**: Cada manual é um arquivo JSON em `servidor/manuais/`, um por modelo do RAB, no formato de [contracts/registro-manual.md](./contracts/registro-manual.md). O comando `python -m servidor.manuais` lê os arquivos, confere cada campo e grava o modelo com `manual_estado = "gravado"`. Arquivo incompleto ou inválido é recusado pelo nome do arquivo e do campo, e não toca os outros modelos. Rodar o comando de novo dá o mesmo banco.
- **Rationale**: O número passa pela revisão do PR antes de entrar no produto, e todo banco novo recebe os mesmos manuais. A carga do RAB já preserva um modelo `gravado` cujo nome é igual ao do extrato, então a ordem entre as duas cargas não importa.
- **Alternatives considered**: Migração do Alembic por lote mistura dado de manual com esquema. Tela de administração deixa o número sem revisão.

## Os 20 modelos

- **Decision**: A lista sai do extrato `dados_aeronaves.csv` carregado em 2026-11-23 no banco local do piloto responsável. Ficam de fora os experimentais RV-10 (412), Adventure, um trike da Ícaros (322), e RV-9A, da Flyer (204). Os 20, na ordem da frota:

| # | Modelo no RAB | Fabricante no RAB | Frota | Motor |
| --- | --- | --- | --- | --- |
| 1 | SR22 | Cirrus Design | 550 | pistão |
| 2 | AT-502B | Air Tractor | 392 | turboélice |
| 3 | EMB-202 | Neiva | 374 | pistão |
| 4 | EMB-203 | Embraer | 372 | pistão |
| 5 | EMB-810D | Embraer | 342 | pistão |
| 6 | EMB-201A | Neiva | 338 | pistão |
| 7 | 182P | Cessna Aircraft | 311 | pistão |
| 8 | EMB-810C | Embraer | 296 | pistão |
| 9 | 58 | Beech Aircraft | 292 | pistão |
| 10 | EMB-202A | Embraer | 280 | pistão |
| 11 | PA-34-220T | Piper Aircraft | 264 | pistão |
| 12 | 152 | Cessna Aircraft | 244 | pistão |
| 13 | A188B | Cessna Aircraft | 223 | pistão |
| 14 | 208B | Textron Aviation | 192 | turboélice |
| 15 | AT-402B | Air Tractor | 188 | turboélice |
| 16 | A36 | Beech Aircraft | 183 | pistão |
| 17 | 210L | Cessna Aircraft | 181 | pistão |
| 18 | PA-46-500TP | Piper Aircraft | 178 | turboélice |
| 19 | AB-115 | Aero Boero | 169 | pistão |
| 20 | EMB-711ST | Neiva | 167 | pistão |

  Se o manual oficial de um desses modelos não tiver cópia pública, ele fica sem manual, e entra o próximo não experimental da frota: EMB-500, 525, C90A, G58, B200GT e assim por diante. A troca fica registrada no PR do lote.
- **Rationale**: É a ordem da frota da constituição, com a regra do experimental da clarificação.
- **Alternatives considered**: Escolher por familiaridade (Cessna e Piper primeiro) fugiria da ordem da frota.

## Que número tirar do manual

- **Decision**: Vazio é o peso vazio padrão da seção de peso e balanceamento. Máximo de decolagem é o da seção de limitações. Bagagem e braço são os do compartimento principal. Combustível é o utilizável. Velocidade e consumo são os da tabela de cruzeiro do manual, a 75% de potência para motor a pistão, ou o cruzeiro recomendado pelo fabricante para turboélice, em atmosfera padrão, na altitude escrita no arquivo. A massa por galão é a que o manual usa no peso e balanceamento. Cada número leva a página.
- **Rationale**: O cálculo existente usa um número só para cada grandeza. A condição escrita evita que o leitor confunda cruzeiro econômico com cruzeiro rápido.
- **Alternatives considered**: Ler a tabela inteira de cruzeiro e escolher pela altitude do voo exigiria mudar o cálculo e a tela, fora desta clarificação.

## Unidade e querosene

- **Decision**: O arquivo guarda o valor como o manual escreve: lb, in, gal, L, kt, mph, gal/h, L/h ou lb/h. O comando converte para kg, m, gal, kt e gal/h com fatores exatos: 1 lb = 0,45359237 kg, 1 in = 0,0254 m, 1 gal americano = 3,785411784 L, 1 mph = 0,868976 kt. Consumo em lb/h vira gal/h pela massa por galão do próprio manual. O modelo ganha `combustivel_kg_por_gal`. O cálculo usa esse valor quando existe e, sem ele, continua com os 2,72 kg/gal de avgas, o que mantém o Cessna 140 igual.
- **Rationale**: Quatro dos 20 modelos (AT-502B, 208B, AT-402B, PA-46-500TP) queimam querosene, mais pesado que avgas. Com 2,72 kg/gal o peso de decolagem sairia menor que o real.
- **Alternatives considered**: Deixar os turboélices sem manual tiraria 950 aviões da lista sem motivo de fonte.
