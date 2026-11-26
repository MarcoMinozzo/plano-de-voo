# Quickstart: Planos DEMO com proxies e ROTAER oficial

## Pré-requisitos

- PostgreSQL 16 de desenvolvimento, com banco normal e banco DEMO distintos.
- Ambiente Python do projeto e dependências instaladas.
- Emenda ROTAER oficial vigente já carregada na base normal.
- Para dados meteorológicos operacionais, integrações oficiais configuradas. A falta de credenciais/cobertura deve aparecer como indisponibilidade, nunca como dado sintético.

## Preparação

Configure fora de arquivos versionados:

```text
APP_ENV=development
DEMO_MODE=1
DATABASE_URL=<URL do banco normal de desenvolvimento>
DATABASE_URL_DEMO=<URL exclusiva do banco DEMO>
```

1. Confirme que as URLs apontam para bases PostgreSQL diferentes e que `APP_ENV` é `development`.
2. Com DEMO habilitado, aplique `alembic upgrade head`; confirme que a migração atingiu somente o banco DEMO.
3. Execute `python -m servidor.importar_rotaer_demo` para copiar somente a emenda vigente e seus aeródromos da base normal. O comando deve recusar URLs ausentes/iguais e ser idempotente. Não execute o carregamento AISWEB para obter novamente a lista já existente.
4. Execute `python -m servidor.semente_demo` para atualizar os 20 perfis genéricos e semear os proxies elegíveis, sem apagar registros ou planos existentes.
5. Execute `flask --app app:criar_app run` e confirme que a seleção apresenta apenas proxies pelo nome do modelo-alvo, sem perfis genéricos ou menus de fontes técnicas; o aviso DEMO fica fora da lista, e a procedência completa aparece no resultado/PDF.
6. Abra `/planos/novo`, selecione um perfil DEMO e use aeródromos da emenda vigente. Confirme que a falta de meteorologia, vento, carta ou pôr do sol é mostrada como indisponibilidade explícita.
7. Abra o resultado e o PDF; ambos devem identificar o uso de dados sintéticos e avisar que o resultado não autoriza voo.
8. Desabilite `DEMO_MODE`; confirme que proxies não aparecem nem são aceitos e que o limite normal continua em 30.

## Verificação automatizada

```bash
uv run pytest tests/test_ambiente_demo.py tests/test_catalogo_aeronaves.py tests/test_tela_piloto.py tests/test_rota_pdf.py
uv run pytest
```

Os testes devem usar banco isolado/fixtures e respostas simuladas; não chamar AISWEB, REDEMET ou serviços meteorológicos reais.
