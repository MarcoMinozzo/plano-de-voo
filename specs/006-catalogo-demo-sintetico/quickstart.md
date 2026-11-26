# Quickstart: Validar catálogo DEMO isolado

## Pré-requisitos

- PostgreSQL 16 local/de desenvolvimento com uma base DEMO de nome diferente da base normal.
- `.venv` e dependências do projeto instaladas.
- Credenciais do AISWEB e caminho do extrato RAB vigente configurados fora do repositório, para carregar fontes oficiais no banco DEMO.

## Preparação

Defina no ambiente, sem gravar segredos em arquivos versionados:

```text
APP_ENV=development
DEMO_MODE=1
DATABASE_URL=<url da base normal de desenvolvimento>
DATABASE_URL_DEMO=<url exclusiva da base PostgreSQL DEMO>
```

1. Confirme que a aplicação recusa DEMO se `APP_ENV` não for `development`, se `DATABASE_URL_DEMO` estiver ausente ou se o nome da base for igual ao da base normal, mesmo com hosts diferentes.
2. Com o modo DEMO habilitado, aplique `alembic upgrade head`; a migração deve atingir somente a base DEMO.
3. Execute `python -m servidor.catalogo` para carregar ROTAER oficial vigente e RAB no banco DEMO.
4. Execute `python -m servidor.semente_demo` para inserir os vinte perfis sintéticos.
5. Execute `flask --app app:criar_app run`; `GET /aeronaves` deve retornar exatamente vinte perfis com procedência `sintetica`.
6. Abra `/planos/novo`; confirme o aviso DEMO e a identificação dos perfis. Com ROTAER vigente no banco DEMO, valide a criação de um plano de teste; sem ROTAER, confirme recusa explícita.
7. Abra o resultado e o PDF; ambos devem identificar os dados sintéticos e preservar o aviso de que não autorizam voo.
8. Desabilite `DEMO_MODE`; no modo normal, confirme que nenhum perfil sintético aparece nem é aceito.

## Verificação automatizada

```bash
uv run pytest tests/test_ambiente_demo.py tests/test_catalogo_aeronaves.py tests/test_tela_piloto.py tests/test_rota_pdf.py
uv run pytest
```
