# Verificação rápida: Corrigir carga do ROTAER

## Testes sem rede

Na raiz do repositório:

```bash
uv run pytest --no-cov tests/test_catalogo_aerodromos.py -q
```

Os testes devem cobrir:

- XML da lista atual com `<item>`, paginação e total;
- detalhes por ICAO com latitude, longitude e `altM`;
- exclusão de helipontos e helidecks;
- falha explícita sem publicar catálogo parcial;
- reutilização de detalhes quando versão e data não mudaram;
- nova consulta quando a versão AISWEB mudou;
- ausência de credenciais em mensagens de erro.

## Verificação operacional

Após preparar o banco e carregar as credenciais fora do repositório, executar:

```bash
.venv/bin/python -m servidor.catalogo
```

Na primeira carga, o comando mostra o progresso da lista e dos detalhes individuais. ROTAER só termina como `disponivel` se todas as páginas e os detalhes necessários forem válidos. Em uma repetição sem alteração das versões AISWEB, os detalhes já validados são reutilizados. O RAB continua exibindo seu próprio estado, independentemente do ROTAER.

Não executar a carga real dentro do pytest.
