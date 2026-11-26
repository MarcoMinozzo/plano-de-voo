# Quickstart: Logo centralizado no login e cadastro

## Pré-requisitos

- Ambiente do projeto instalado.
- `DATABASE_URL_TESTE` aponta para a base descartável de testes; a fixture de pytest recria suas tabelas.
- Dependências Node já instaladas para a compilação Tailwind.

## Validação automatizada

```bash
uv run --no-sync pytest --no-cov tests/test_casca_visual.py
npm run css:build
git diff --check
```

Resultado esperado: testes verificam presença única, posição no cartão, largura, ausência no cabeçalho público e permanência do emblema no cabeçalho autenticado; CSS compila e não há erros de whitespace.

## Inspeção manual

1. Abrir `/entrar` e `/cadastro` em larguras de 390 px e 1440 px.
2. Confirmar o logo no cartão, centralizado acima do título, sem segundo logo no cabeçalho e sem rolagem horizontal.
3. Entrar e abrir uma página autenticada; confirmar que o logo do cabeçalho permanece.
4. Confirmar que os campos, mensagens, links e envio dos formulários continuam funcionando.
