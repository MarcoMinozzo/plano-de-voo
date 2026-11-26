# Data Model: Filtro integrado na seleção de aeródromos

Esta feature não adiciona nem altera entidades persistidas.

## Valor selecionado

- Origem e destino continuam sendo identificadores de aeródromos já existentes no catálogo.
- O texto de busca e a opção ativa são estado transitório da interface.
- O formulário envia `origem` e `destino` com os identificadores selecionados; texto livre não representa uma seleção.
- A validação do servidor, o banco de dados e o cálculo da rota permanecem inalterados.
