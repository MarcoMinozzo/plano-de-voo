# Quickstart: Aumentar logo no login

## Pré-requisitos

- Dependências Python do projeto instaladas.
- `DATABASE_URL_TESTE` configurada para a base descartável de testes; a fixture de pytest recria as tabelas.
- Dependências Node já instaladas para a compilação Tailwind.

## Validação automatizada

```bash
uv run --no-sync pytest --no-cov tests/test_casca_visual.py
npm run css:build
git diff --check
```

Resultado esperado: o logo do login mede 103,68 px e permanece centralizado; o logo do cadastro permanece em 86,4 px; as páginas autenticadas preservam o logo no cabeçalho; o CSS compila sem erro.

## Inspeção visual

1. Abrir `/entrar` em 390 px e 1440 px.
2. Confirmar que o logo está maior, centralizado acima do título, inteiro dentro do cartão e sem rolagem horizontal.
3. Abrir `/cadastro` e confirmar que o logo conserva a dimensão anterior.
4. Abrir uma página autenticada e confirmar que o cabeçalho continua igual.
