# Quickstart: Atualizar meteorologia ao consultar o plano

## Pré-requisitos

- Ambiente virtual e dependências do projeto restaurados.
- Banco de teste isolado conforme `documentacao/operacao.md`.
- Os testes devem simular AWC e REDEMET; não dependem de credenciais nem de disponibilidade externa.
- Para conferência de radar real, configure uma chave REDEMET válida fora do repositório. Sem ela, o estado esperado é indisponível.

## Validação automatizada

```bash
uv run pytest -q tests/test_tempo.py tests/test_tela_piloto.py
git diff --check
```

## Cenários

1. Abra um plano salvo após configurar resposta simulada mais recente; confirme que a página e o JSON mostram a resposta atual e preservam os trechos já gravados.
2. Use trechos com aeródromo repetido; confirme uma consulta METAR e uma consulta TAF por indicativo distinto, sem novas consultas ao alternar fichas ou camadas.
3. Simule AWC sem observação para um aeródromo e com METAR para outro; confirme indisponibilidade apenas no primeiro.
4. Remova `REDEMET_API_KEY`; confirme que o plano continua abrindo, radar está desativado e o motivo informa ausência da chave.
5. Simule radar válido com chave de teste; confirme que o controle é habilitado somente com URL e limites geográficos válidos.
6. Simule timeout em uma fonte; confirme que os resultados válidos das outras fontes permanecem disponíveis e que rota, cálculos e aceitabilidade não mudam.

## Conferência manual

Abra um plano existente no navegador e confirme fonte e horário dos boletins atuais. Na configuração local atual, espere ver o radar indisponível até uma chave REDEMET ser configurada; não use dados sintéticos como substituição.
