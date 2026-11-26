# Pesquisa: redesenho do menu principal

## Decisões

### Reutilizar a aparência dos cards existentes

- **Decisão**: usar o azul semitransparente `aviation-glass`, com os mesmos cantos arredondados e tratamento de vidro dos cards atuais.
- **Fundamento**: o token já corresponde ao pedido de manter o tom azul e semitransparente.
- **Alternativa considerada**: adicionar um novo token ou dependência visual. Rejeitada por duplicar estilo existente.

### Manter o menu em 70% e permitir quebra em telas estreitas

- **Decisão**: manter a largura de 70% também em telas estreitas; preservar o logo ao lado conforme escolha do usuário e permitir que os quatro itens quebrem linha.
- **Fundamento**: o usuário confirmou essa prioridade para telas estreitas.
- **Alternativa considerada**: ampliar o menu em celular e posicionar o logo acima. Rejeitada pelo usuário.

### Mover a impressão para o resumo do plano

- **Decisão**: retirar a ação do cabeçalho global e colocá-la no card inicial `#resumo`, apontando para o PDF do mesmo plano.
- **Fundamento**: a rota do plano fornece seu identificador e já possui um card de resumo destacado.
- **Alternativa considerada**: colocá-la na tabela do painel. Rejeitada pelo usuário.

## Escopo técnico

Não há dados, APIs, dependências ou estados novos. Os rótulos existentes e o formulário POST de saída serão preservados.
