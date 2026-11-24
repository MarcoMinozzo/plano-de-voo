# Contract: Tela do piloto

O que o piloto vê e devolve. A conta da rota não entra neste contrato.

## Formulário de plano

Campos: aeronave, origem, destino, hora de partida, ocupantes, peso do piloto, peso do passageiro, bagagem, combustível a bordo. A confirmação de hora passada só entra quando a hora informada já passou.

Quando a conta recusa, a resposta mostra a mensagem e os mesmos campos preenchidos.

Origem e destino não são a lista nacional. O piloto digita um texto. Com menos de dois caracteres úteis, não há correspondências. Com dois ou mais, a resposta lista só aeródromos de avião da emenda vigente cujo identificador ou nome contém o texto, cada um com identificador e nome. Sem emenda, a resposta diz que o catálogo nacional está indisponível e não lista lugar.

## Alteração

A partir de um plano do piloto, a alteração mostra o formulário com os valores desse plano. Confirmar recalcula o mesmo plano. Recusa de formulário não substitui o plano gravado e devolve os valores digitados. Plano de outro piloto recebe a mesma recusa de acesso já usada quando o plano não pode ser mostrado.

## Leitura do plano

No painel e na tela do plano:

- estado interno aceito pela conta: "aceitável para planejamento"
- estado interno não aceito: "não aceitável"
- na tela do plano não aceitável, o motivo visível

A tabela de grandezas só é mostrada quando existe ao menos uma grandeza, com valor, unidade e fonte.

Junto do mapa de ruas, quando ele é mostrado: o mapa só situa a rota e o radar e não substitui a carta de voo visual. A carta disponível é nomeada como carta de voo visual, com a fonte. Sem carta, a palavra é "indisponível". Tempo, vento, radar e pôr do sol sem dado usam a mesma palavra.

## Checklist

Marcar ou desmarcar grava o item do plano do piloto. A tela seguinte mostra esse item, com o estado novo, sem exigir que o piloto o procure no topo. Item de plano de outro piloto não muda.
