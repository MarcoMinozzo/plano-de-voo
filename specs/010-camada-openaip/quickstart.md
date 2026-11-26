# Quickstart — Camada aeronáutica OpenAIP

## Pré-requisitos

- Ambiente local e banco configurados conforme
  [documentacao/operacao.md](../../documentacao/operacao.md).
- Sessão autenticada e plano próprio com pelo menos dois pontos de rota.
- Chave OpenAIP válida configurada apenas no ambiente local em `.env`.
- Uso e distribuição compatíveis com CC BY-NC 4.0.

## Testes automatizados

```sh
uv run pytest --no-cov tests/test_openaip.py tests/test_tela_piloto.py
```

Os testes devem simular o provedor, não usar uma chave real e cobrir: tile
válido; zoom e coordenadas inválidos; ausência ou recusa da chave; timeout e
resposta não PNG; plano próprio e plano de outro piloto; seletor, atribuição,
radar independente e rota preservada.

## Validação manual

1. Configure uma chave válida no arquivo local `.env`, sem a copiar para
   arquivos versionados ou mensagens.
2. Abra um plano próprio e confirme que ruas permanecem selecionadas e radar
   desligado.
3. Selecione OpenAIP; confirme que tiles aparecem, a atribuição com link fica
   visível e o rótulo deixa claro que não é WAC nem fonte oficial.
4. Ligue e desligue radar; confirme que a base OpenAIP e a rota permanecem.
5. Selecione ruas e volte para OpenAIP; confirme que a seleção é explícita e
   não altera dados ou zoom da rota.
6. Repita sem chave e com falha simulada: a interface informa indisponibilidade
   e não troca automaticamente para ruas ou AISWEB.
7. Repita em 390 px e 1440 px, usando teclado e toque. Não mostrar credencial
   em HTML, URL, mensagens ou logs.

## Resultado esperado

OpenAIP é uma base aeronáutica comunitária opcional. A carta WAC oficial
continua separada e sujeita aos seus próprios gates. Nenhum tile afeta o
cálculo do plano.
