# Quickstart: Enxugar informações da página do plano

## Validação automatizada

```bash
uv run pytest -q tests/test_rota_pdf.py
git diff --check
```

## Cenários

1. Abra um plano sintético e confirme que estado, aviso extenso, alvo do exercício, hipótese de reabastecimento e tabela de fontes não aparecem em nenhuma parte da página, inclusive na orientação expansível.
2. Confirme que motivos, alertas, aeronave, trechos e aviso geral didático continuam disponíveis na página.
3. Gere o PDF e confirme que o aviso sintético e a proveniência continuam presentes.
4. Confirme que o estado, os resultados e a proveniência persistidos não foram alterados pela abertura da página.
