# Data Model: Clarear a tela do piloto

Nenhuma entidade nova e nenhuma coluna nova.

## Plano de voo

Continua pertencendo a um piloto. Origem, destino, hora, aeronave, dados particulares, estado interno, motivo, trechos e itens de checklist já estão gravados.

O que muda é de leitura:

- O estado interno `calculado` é lido como "aceitável para planejamento".
- O estado interno `inaceitavel` é lido como "não aceitável".
- A falta de fonte é lida como "indisponível".

## Valor informado

Não é coluna. É o que o piloto enviou neste pedido e a tela mostra de volta quando a conta recusa: aeronave, origem, destino, hora, ocupantes, pesos, combustível a bordo e, se a hora já passou, a confirmação.

## Correspondência de aeródromo

Não é coluna. É a lista curta, já filtrada no servidor, de aeródromos de avião da emenda vigente cujo identificador ou nome contém o texto digitado.

## Item de checklist

Já guarda texto, fonte e se está marcado. A tela passa a reapresentar o item marcado à vista.
