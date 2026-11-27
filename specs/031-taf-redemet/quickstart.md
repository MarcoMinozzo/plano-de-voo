# Quickstart: Priorizar TAF da REDEMET

## Testes focados

```bash
uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py tests/test_rota_pdf.py -k 'taf or meteorologia'
git diff --check
```

## Cenários de validação

1. REDEMET retorna múltiplos TAF válidos para SBMT; confirmar seleção da mensagem mais recente, fonte REDEMET e horários.
2. REDEMET sem chave, vazia, inválida ou com falha; confirmar fallback AWC para o mesmo ICAO.
3. Ambas as fontes sem TAF válido; confirmar indisponibilidade explícita e METAR preservado.
4. Resposta REDEMET com outro ICAO ou horários inválidos; confirmar rejeição.
5. Conferir ficha, tabela de fontes e PDF para correspondência entre mensagem exibida, fonte e data.

Os testes devem usar respostas simuladas. A consulta ao provedor ao vivo é opcional e não deve imprimir nem registrar a chave.
