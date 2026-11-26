# Quickstart — Mapa interativo com carta e radar

## Pré-requisitos

- Ambiente local e banco configurados conforme [documentacao/operacao.md](../../documentacao/operacao.md).
- Sessão autenticada e plano com pelo menos dois pontos de rota.
- Chaves existentes para as fontes que exigem autenticação mantidas somente no ambiente, nunca em arquivos versionados.

## Validação automatizada

Executar os testes focados:

```sh
uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py
```

Os testes devem usar dados simulados e não depender de acesso externo. Cobrir os estados da carta indisponível, estados do radar, propriedade do plano e apresentação de METAR/TAF. Não criar testes de parser ou endpoint WMS, que não fazem parte do caminho aprovado.

## Validação manual

1. Abrir um plano de teste com origem e destino e ao menos dois pontos.
2. Confirmar que ruas estão selecionadas, radar desligado e rota/zoom visíveis.
3. Confirmar que a carta permanece indisponível enquanto os gates da fonte GeoPDF não estiverem aprovados.
4. Ligar e desligar radar sobre ruas; se a carta tiver passado por todos os gates, repetir sobre a carta. Confirmar que a base e a rota não mudam.
5. Simular/observar carta sem acesso, radar ausente ou limites inválidos; confirmar mensagem indisponível sem fallback silencioso.
6. Confirmar METAR/TAF agrupados por aeródromo/tipo, texto bruto identificável, campos existentes, fonte/horário quando fornecidos e ausência explícita.
7. Repetir em 390 px e 1440 px, usando teclado e toque. O aviso educacional permanece visível.
8. Antes de qualquer implementação da carta, verificar e registrar os quatro gates em [research.md](./research.md): PDF vigente exato, georreferenciamento e cobertura da rota, autorização para derivados e ambiente reproduzível de geração de tiles. Não contornar o desafio Cloudflare. Se qualquer gate não puder ser comprovado, a carta continua indisponível; não usar a amostra de 2020.

## Resultado esperado

Trocas de camada não fazem novo cálculo de rota. Falhas externas não travam a abertura do plano nem mostram uma camada incorreta como carta.
