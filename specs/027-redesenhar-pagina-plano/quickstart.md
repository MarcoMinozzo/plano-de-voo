# Quickstart: Redesenho da página do plano

## Testes automatizados

```bash
npm run css:build
uv run pytest --no-cov tests/test_tela_piloto.py tests/test_tempo.py tests/test_catalogo_aerodromos.py
git diff --check
```

Verificar os modelos em PostgreSQL aplicando e revertendo a migração de contatos no ambiente de teste.

## Verificação visual

1. Abrir um plano de teste com escalas e confirmar a rota completa no primeiro card e nomes de aeródromos nas fichas.
2. Conferir os dados ROTAER e um contato publicado; usar um registro sem contato para confirmar o estado indisponível.
3. Conferir alertas de excesso de peso e limite fora do tolerado em vermelho, com texto legível.
4. Em 390 px e 1440 px, testar o card, as abas e os controles do mapa por toque e teclado; confirmar a largura de aproximadamente 80% no viewport largo.
5. Testar ruas, Google desativado sem chave, REDEMET e RainViewer separadamente. Confirmar rota preservada, base legível, overlay alinhado, crédito/horário/cobertura do RainViewer e ausência da máscara cinza.
6. Confirmar WAC indisponível em estado compacto, ausência de aviso OpenAIP sem chave, ausência de “Como ler este plano” e de link PDF no rodapé; manter impressão no topo e aviso didático geral.
