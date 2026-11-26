# Research: Catálogo sintético isolado para DEMO

## Decisões

### 1. O modo DEMO seleciona somente o banco PostgreSQL DEMO

- **Decisão**: Um helper comum valida `DEMO_MODE`, `APP_ENV`, `DATABASE_URL` e `DATABASE_URL_DEMO`; só retorna a URL DEMO quando o modo DEMO foi solicitado explicitamente, o ambiente é `development`, e o banco DEMO difere do banco normal. Aplicação, Alembic e comandos de carga reutilizam essa decisão. Não há fallback.
- **Evidência**: `app.py` configura o banco diretamente por `DATABASE_URL`; `alembic/env.py`, `servidor/catalogo.py` e `servidor/semente.py` também escolhem a URL diretamente. `servidor/__init__.py:carregar_env` lê `.env` por `setdefault`, sem resolver modos.
- **Alternativas consideradas**: Trocar manualmente `DATABASE_URL` para executar o DEMO foi rejeitado por facilitar conexão acidental com produção; usar SQLite foi rejeitado pela constituição, que exige PostgreSQL para o runtime.

### 2. Procedência sintética é um tipo próprio, nunca uma fonte secundária

- **Decisão**: Acrescentar `sintetica` ao tipo de fonte, permitir ausência de data de publicação somente para esse tipo, e validar/selecionar essa procedência apenas quando a aplicação estiver em DEMO. A data de consulta registra geração/carga, não uma publicação.
- **Evidência**: `servidor/proveniencia.py` atualmente aceita apenas `oficial` e `secundaria`, exige `data_publicacao` e escolhe fontes por recência editorial. `FonteTecnicaAeronave` e sua constraint Alembic refletem essas mesmas regras.
- **Alternativas consideradas**: Marcar o perfil como fonte secundária ou atribuir uma data de publicação fictícia foi rejeitado porque apresentaria uma origem inexistente como rastreável.

### 3. A semente DEMO é separada e posterior à carga oficial

- **Decisão**: Criar `servidor/semente_demo.py`, idempotente e limitado a `DATABASE_URL_DEMO`. Carregar ROTAER/RAB oficial no banco DEMO antes da semente sintética; associar os perfis a um registro DEMO próprio do extrato, mais recente que o carregamento oficial, sem alterar a semente normal.
- **Evidência**: `servidor/catalogo.py:modelos_visiveis` filtra aeronaves pelo extrato disponível mais recente; `servidor/semente.py:semear` é a semente normal e inclui somente os dados históricos existentes.
- **Alternativas consideradas**: Inserir perfis no `servidor/semente.py` foi rejeitado porque misturaria dados fictícios com a base normal e com a semente histórica.

### 4. DEMO não cria dados de navegação nem condições de voo

- **Decisão**: Exigir emenda ROTAER oficial vigente no próprio banco DEMO para criar rota; deixar meteorologia, vento, carta e pôr do sol sujeitos às mesmas fontes oficiais e estados indisponíveis já existentes.
- **Evidência**: A constituição exige origem ROTAER vigente e proíbe inventar coordenadas, boletim, vento, carta ou radar. O usuário confirmou o uso da emenda oficial vigente no banco DEMO.
- **Alternativas consideradas**: Gerar aeródromos ou condições sintéticas foi rejeitado por contrariar a constituição e ampliar risco de confusão operacional.

## Referências internas consultadas

- `app.py`, `servidor/modelos.py`, `servidor/catalogo.py`, `servidor/proveniencia.py`, `servidor/planos.py`
- `servidor/semente.py`, `servidor/catalogo_rab.py`, `alembic/env.py`
- `tests/conftest.py`, `tests/conftest_rota.py`, `tests/test_catalogo_aeronaves.py`, `tests/test_rota_pdf.py`
- `.specify/memory/constitution.md`, `.cursor/rules/speckit-sdd.mdc`
