# Quickstart: Filtro integrado na seleção de aeródromos

## Verificação automatizada

```sh
uv run pytest --no-cov tests/test_tela_piloto.py -q
```

Esperado: os testes verificam os dois campos combinados, busca parcial por código e nome sem considerar caixa/acento, seleção que envia o identificador correto, rejeição de texto livre e valores restaurados após validação.

## Verificação manual

1. Abra Novo voo com catálogo nacional e com catálogo local.
2. Em Origem e Destino, digite parte do código e parte do nome, incluindo um nome acentuado digitado sem acento.
3. Escolha um resultado com teclado e com toque/clique.
4. Confirme que não há controles separados de filtro e que a seleção mostra código e nome.
5. Tente enviar texto que não corresponde a uma opção; a interface deve pedir uma seleção válida.
6. Reapresente o formulário após uma validação e confirme que origem e destino continuam preenchidos.
7. Desative JavaScript e confirme que os seletores nativos continuam permitindo escolher origem e destino.
