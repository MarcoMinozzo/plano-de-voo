# Validação rápida: menu principal

## Verificações automatizadas

```bash
npm run css:build
.venv/bin/pytest -q --no-cov tests/test_casca_visual.py
git diff --check
```

## Inspeção visual

- Abrir uma página autenticada em 390 px e 1440 px.
- Confirmar logo de 108 px fora do card e card de navegação de 70% da viewport.
- Confirmar os quatro rótulos em maiúsculas e quebras sem overflow horizontal.
- Abrir `/planos/<id>` e confirmar “IMPRIMIR VOO” dentro do card de resumo, apontando ao PDF do mesmo plano.
- Confirmar que a ação Sair continua submetendo POST.
