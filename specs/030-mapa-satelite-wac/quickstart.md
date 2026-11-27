# Quickstart — Validação das camadas do mapa

## Pré-requisitos

- Ambiente local e dependências já instalados conforme `documentacao/operacao.md`.
- Para conferir a camada ao vivo, sessão de piloto e `REDEMET_API_KEY` configurada fora do repositório. Testes automatizados usam mocks e não exigem a chave.

## Validação automatizada focada

```bash
uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py -k 'satelite or mapa or wac'
npm run css:build
git diff --check
```

Esperado: casos de resposta válida/inválida, autorização, não exposição da chave, estados dos controles e tamanho do mapa passam; o build gera o CSS atualizado sem erros.

## Validação visual

1. Abrir um plano próprio e confirmar mapa quadrado numa viewport desktop de 1440 px.
2. Em viewport de 390 px, confirmar que altura atual, botões e zoom permanecem utilizáveis, sem rolagem horizontal.
3. Ativar Satélite; confirmar fonte e horário do frame, rota visível, e radar ainda independente. Desativar Satélite e confirmar remoção apenas dessa camada.
4. Com a fonte simulada indisponível, confirmar mensagem acessível e ausência de imagem.
5. Confirmar que Carta WAC está sempre visível; quando indisponível, fica desabilitada e não apresenta mapa de ruas ou PDF como camada.
6. Confirmar que documentos AISWEB válidos continuam abrindo no diálogo existente.
