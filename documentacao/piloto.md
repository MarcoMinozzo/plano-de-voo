# Plano de voo

## Orientação ao piloto

Este texto acompanha o relatório impresso.

## O que você informa

Informe de onde sai, para onde vai, a data e a hora, e o tipo de avião. Informe o número de passageiros, já incluindo você, o peso das pessoas e o peso da bagagem. O combustível de planejamento vem do manual da aeronave.

Seu nome de exibição pode ser alterado em Perfil e aparece na capa do relatório PDF. Ele é independente da identificação usada para entrar. Depois de salvar, a tela confirma a alteração.

## Meteorologia, vento, carta e radar

O primeiro card mostra a rota completa, com os nomes oficiais dos aeródromos, coordenadas e elevação. As fichas usam os indicativos ICAO nos títulos e mostram os nomes completos em cada trecho. Telefone e e-mail publicados no ROTAER/AISWEB ficam na seção correspondente do PDF; um campo não publicado aparece como indisponível.

O plano tem uma ficha para cada trecho. A ficha mostra os METARs da saída e da chegada daquele trecho, com os campos estruturados disponíveis identificados em português e nas unidades informadas. O METAR e o TAF originais permanecem visíveis sem tradução. Códigos não decodificados não recebem interpretação inventada.

Quando o aeródromo não publica METAR, a ficha pode mostrar o METAR regional mais próximo, somente se a estação estiver a até 50 NM. A ficha identifica a estação observadora, o indicativo, a distância e o horário UTC; essa observação não confirma as condições do aeródromo ou da pista. O TAF continua sendo consultado exclusivamente para o aeródromo indicado.

METAR e TAF são consultados novamente quando você abre um plano salvo. O radar só é consultado quando ativado no mapa. Essas consultas não alteram a rota nem os cálculos. Os dados podem continuar indisponíveis quando não houver boletim ou cobertura; a tela informa a indisponibilidade em vez de apresentar um boletim antigo como atual.

O vento de área da rota, quando disponível, mostra a direção de onde vem, a velocidade e o efeito no voo. O controle “Carta WAC” abre os PDFs oficiais correspondentes quando disponíveis; um PDF não é tratado como camada georreferenciada. A opção permanece visível e fica desabilitada com indicação de indisponibilidade quando não há documento AISWEB validado. Sem carta utilizável, o mapa de ruas permanece como base cartográfica. A fonte e os metadados dos valores ficam em uma seção separada do PDF.

O único controle “Radar de chuva” usa a composição RainViewer, que reúne várias redes e cobre mais área do que o quadro único da REDEMET. A interface identifica que é uma fonte não oficial e mostra crédito com link, horário do frame e ressalva de cobertura. A imagem da REDEMET só entra se a RainViewer não puder ser carregada. Se a camada falhar, é removida e o estado acessível informa a indisponibilidade.

O controle “Satélite REDEMET” carrega sob demanda a imagem de satélite mais recente validada, identificando fonte e horário. É uma sobreposição independente do radar; se a imagem ou seus limites não puderem ser validados, a camada não aparece e a tela informa a indisponibilidade.

## Item indisponível

METAR, TAF, vento, contato, coordenadas, carta ou radar podem aparecer como indisponíveis na ficha ou no mapa. Isso quer dizer que o dado não foi fornecido ou não pôde ser validado. O sistema não completa esse buraco com um valor estimado nem usa o mapa de ruas como substituto da carta. Sem vento da rota, o plano não mostra uma velocidade em relação ao solo como se o vento fosse calmo. O resto do plano continua visível. Use o plano sabendo qual parte faltou.

## Escala

Uma escala é um aeródromo de avião da emenda vigente, entre a origem e o destino, escolhido pelo sistema. A rota fica com o menor tempo de voo. Se o tempo empata, fica a rota com menos escalas. Se o empate continuar, fica a mais curta.

Em cada escala, a hipótese de planejamento é reabastecer até o combustível de planejamento da aeronave. O relatório identifica a hipótese sem misturá-la às fontes; a procedência fica no modal e no apêndice separado do PDF. Não é um abastecimento lançado no pátio.

## Catálogo indisponível

O catálogo de aeródromos usa os aeródromos de avião da emenda vigente. Se essa emenda não puder ser consultada, fica indisponível; o sistema não completa a lista com coordenada estimada.

## Seleção de aeronaves

A caixa mostra no máximo os 30 modelos factuais completos mais comuns na ordem de frota do extrato vigente do RAB. Para ser completo, o modelo precisa de combustível utilizável, velocidade e consumo do mesmo perfil nominal, peso vazio, peso máximo de decolagem e limite de bagagem, todos com unidade e fonte rastreável, oficial ou secundária.

Sem extrato RAB vigente, o catálogo factual fica indisponível; perfis sintéticos didáticos permanecem em uma categoria separada e não são contados entre os modelos factuais.

## Perfis sintéticos didáticos

Os perfis sintéticos didáticos mantêm valores e unidades para exercícios de software. A associação a um modelo é somente o alvo do exercício e não comprova aplicabilidade. Os valores não foram validados e não são dados factuais daquele modelo. O aviso “perfil sintético didático — valores não validados; não representam dados do modelo associado” aparece na seleção, no resultado e no PDF. O catálogo de aeródromos e o cálculo da rota continuam sujeitos à emenda oficial vigente do ROTAER; dados sintéticos não substituem aeródromos, vento, meteorologia, carta ou pôr do sol.

## Limite do plano

O resultado é apoio ao planejamento de um voo visual. Não substitui o manual da aeronave, o treinamento de voo nem a norma vigente. Não é autorização de voo.
