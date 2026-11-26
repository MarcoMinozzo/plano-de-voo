# Research: Filtro integrado na seleção de aeródromos

## Decisão

Usar a lista de aeródromos já renderizada pela tela e fazer a busca no próprio campo de origem ou destino. O campo exibe o código e o nome escolhidos, mas o formulário continua enviando somente o identificador do aeródromo.

## Evidências e justificativa

- `EXPERIENCE.md` já define que, com mais de doze aeródromos, o texto do campo de seleção filtra pelo código ou nome exibido.
- `templates/plano_novo.html` atualmente apresenta filtros independentes, seletores nativos e uma busca local que ignora caixa e acentuação.
- `tests/test_tela_piloto.py` já valida a busca por código e nome sem acentos e pode ser ampliado para cobrir a interação combinada.
- O formulário usa os campos `origem` e `destino`; a API, o catálogo e o cálculo não precisam mudar.

## Alternativas consideradas

- Manter os filtros como campos separados: rejeitada porque contradiz o pedido e a experiência já definida.
- Usar busca remota a cada tecla: rejeitada porque o catálogo está disponível na página e a busca local evita chamadas adicionais.
- Enviar o texto digitado como código: rejeitada porque permitiria valores que não correspondem a uma opção do catálogo.

Não há questões técnicas pendentes nem necessidade de pesquisa externa.
