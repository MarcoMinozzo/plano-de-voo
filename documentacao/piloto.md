# Plano de voo

## Orientação ao piloto

Este texto aparece na tela do plano e no PDF.

## O que você informa

Informe de onde sai, para onde vai, a data e a hora, e o tipo de avião. Informe o número de passageiros, já incluindo você, o peso das pessoas e o peso da bagagem. O combustível de planejamento vem do manual da aeronave.

Seu nome de exibição pode ser alterado em Perfil e aparece na capa do relatório PDF. Ele é independente da identificação usada para entrar. Depois de salvar, a tela confirma a alteração.

## Meteorologia, vento, carta e radar

O plano tem uma ficha para cada trecho. A ficha mostra os METARs da saída e da chegada daquele trecho, com os campos estruturados que a fonte fornece identificados em português e nas unidades da fonte. O horário e a fonte aparecem junto aos dados, e o METAR original permanece visível sem tradução. Códigos não decodificados não recebem interpretação inventada. O TAF é apresentado separadamente, em seu texto original.

O vento de área da rota, quando disponível, mostra a direção de onde vem, a velocidade e o efeito no voo. A carta oficial de voo visual (WAC) permanece indisponível até que edição vigente, georreferenciamento, cobertura, autorização e entrega reproduzível sejam validados; ela não é substituída por outra camada. O mapa de ruas apenas situa o trecho. OpenAIP é uma camada comunitária não oficial, não é uma carta WAC e não valida nem autoriza a rota. O radar começa desligado e pode ser ligado independentemente da base escolhida. Se estiver indisponível, a tela informa se falta a chave REDEMET, se não há cobertura válida para o trecho ou se a fonte falhou; a camada permanece desligada.

## Item indisponível

METAR, TAF, vento, carta, coordenadas, OpenAIP ou radar podem aparecer como indisponíveis na ficha ou no mapa. Isso quer dizer que a fonte não entregou o dado, que falta cobertura ou coordenada, ou que a camada ainda não passou pelos critérios de validação. O sistema não completa esse buraco com um valor estimado nem usa ruas ou OpenAIP como substituto da carta. Sem vento da rota, o plano não mostra uma velocidade em relação ao solo como se o vento fosse calmo. O resto do plano continua visível. Use o plano sabendo qual parte faltou.

## Escala

Uma escala é um aeródromo de avião da emenda vigente, entre a origem e o destino, escolhido pelo sistema. A rota fica com o menor tempo de voo. Se o tempo empata, fica a rota com menos escalas. Se o empate continuar, fica a mais curta.

Em cada escala, a hipótese de planejamento é reabastecer até o combustível de planejamento do manual da aeronave. A tela e o PDF mostram essa hipótese junto com a fonte do manual. Não é um abastecimento lançado no pátio.

## Catálogo indisponível

O catálogo de aeródromos usa os aeródromos de avião da emenda vigente. Se essa emenda não puder ser consultada, fica indisponível; o sistema não completa a lista com coordenada estimada.

## Seleção de aeronaves

A caixa mostra no máximo os 30 modelos factuais completos mais comuns na ordem de frota do extrato vigente do RAB. Para ser completo, o modelo precisa de combustível utilizável, velocidade e consumo do mesmo perfil nominal, peso vazio, peso máximo de decolagem e limite de bagagem, todos com unidade e fonte rastreável, oficial ou secundária.

Sem extrato RAB vigente, o catálogo factual fica indisponível; perfis sintéticos didáticos permanecem em uma categoria separada e não são contados entre os modelos factuais.

## Perfis sintéticos didáticos

Os perfis sintéticos didáticos mantêm valores e unidades para exercícios de software. A associação a um modelo é somente o alvo do exercício e não comprova aplicabilidade. Os valores não foram validados e não são dados factuais daquele modelo. O aviso “perfil sintético didático — valores não validados; não representam dados do modelo associado” aparece na seleção, no resultado e no PDF. O catálogo de aeródromos e o cálculo da rota continuam sujeitos à emenda oficial vigente do ROTAER; dados sintéticos não substituem aeródromos, vento, meteorologia, carta ou pôr do sol.

## Limite do plano

O resultado é apoio ao planejamento de um voo visual. Não substitui o manual da aeronave, o treinamento de voo nem a norma vigente. Não é autorização de voo.
