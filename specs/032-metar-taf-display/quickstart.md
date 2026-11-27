# Quickstart: Apresentação legível de METAR e TAF

## Validação automatizada

```bash
uv run pytest --no-cov tests/test_tempo.py tests/test_tela_piloto.py
npm run css:build
git diff --check
```

## Cenários

1. METAR com vento variável, visibilidade, `-RA` e nuvens: confirmar campos, unidades e explicação em português.
2. TAF com grupos base, FM, BECMG, TEMPO e PROB: confirmar períodos distintos e campos associados ao grupo correto.
3. Código conhecido combinado (por exemplo, intensidade + descritor + chuva): confirmar código original e explicação composta.
4. Token meteorológico desconhecido: confirmar indicação de não interpretado, sem descrição inventada.
5. Confirmar que os boletins brutos continuam idênticos em blocos escuros monoespaçados.
6. Abrir a página em viewport de 390 px e confirmar que a rolagem horizontal, se necessária, fica dentro da tabela.

Os testes devem usar dados simulados; não é necessário consultar AWC ou outra API ao vivo.
