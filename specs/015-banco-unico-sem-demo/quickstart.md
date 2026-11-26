# Quickstart: Banco único e perfis sintéticos didáticos

## Pré-requisitos

- Ambiente virtual do projeto instalado.
- `DATABASE_URL_TESTE` aponta para uma base descartável, distinta da base de
  produto.
- Não use uma URL de produto nos testes.

## Validar comportamento

Execute os testes de configuração, perfis, migração, proveniência e PDF:

```bash
.venv/bin/pytest tests/test_ambiente.py tests/test_perfis_sinteticos.py tests/test_importar_perfis_sinteticos.py tests/test_proveniencia.py tests/test_rota_pdf.py
```

O resultado esperado é que a configuração de produto use uma única base; os
testes permaneçam isolados; os vinte proxies apareçam sem perfis genéricos;
valores e unidades sejam preservados; e os avisos apareçam na interface e no
PDF.

Os testes da migração usam duas bases descartáveis e verificam repetição,
conflitos, origem incompleta e ausência de alterações na origem. Não execute
o importador contra as bases reais como parte da suíte.

## Operação da migração real

A migração deve ser executada uma única vez, sob decisão explícita do
operador, com `DATABASE_URL` apontando para a base canônica e
`DATABASE_URL_DEMO_ORIGEM` para a base antiga. Antes de executar, confirme as
duas URLs e faça backup do destino. O comando não apaga nem modifica a origem.
