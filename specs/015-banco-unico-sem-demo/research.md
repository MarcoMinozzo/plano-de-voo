# Pesquisa: Banco único e perfis sintéticos didáticos

## Decisões

### Manter a base atual do produto como destino

- **Decisão**: A base configurada atualmente para o produto continua canônica;
  a importação não copia nem substitui ROTAER, RAB ou dados de piloto/plano.
- **Motivo**: O usuário confirmou que ROTAER e RAB já foram carregados. A antiga
  base DEMO possui cópia do ROTAER e um extrato RAB sintético, que não devem
  substituir os dados canônicos.
- **Alternativas**: Copiar todos os catálogos da base antiga ou trocar a base
  canônica. Ambas podem sobrescrever dados existentes e foram descartadas.

### Importar os proxies existentes, sem recalcular

- **Decisão**: Copiar exatamente os vinte registros `proxy_sintetico` e seus
  seis registros de fonte por perfil. Não copiar os vinte genéricos, o extrato
  RAB sintético, pilotos ou planos. Remapear IDs e deixar `extrato_id` nulo.
- **Motivo**: `Aeronave.extrato_id` aceita nulo e os proxies devem ficar
  separados do catálogo factual. O usuário pediu preservar os valores atuais
  sem pesquisa ou validação aeronáutica.
- **Alternativas**: Regerar valores com a semente ou importar a base inteira.
  Regerar pode divergir dos dados que o usuário quer manter; importar tudo
  traria registros fora do escopo.

### Tornar a importação repetível e não destrutiva

- **Decisão**: Usar a identidade do proxy e comparar os valores e unidades
  existentes. Registros idênticos tornam a repetição um no-op; divergência ou
  origem incompleta aborta a transação e identifica o motivo.
- **Motivo**: `Aeronave.nome` não tem unicidade de banco e uma repetição não
  pode duplicar perfis nem sobrescrever um modelo factual.
- **Alternativas**: Inserção cega por ID ou atualização automática por nome;
  ambas arriscam colisão e perda de dados.

### Manter os vinte proxies distintos do catálogo factual

- **Decisão**: Exibir os proxies em categoria didática própria, sem contá-los
  no limite de trinta modelos factuais nem submetê-los à validação de fonte.
- **Motivo**: O catálogo factual continua sujeito ao RAB e a fontes; os
  proxies são exercícios sintéticos e não afirmam correspondência técnica.
- **Alternativas**: Misturar as duas listas ou retirar os proxies quando o RAB
  estiver indisponível; ambas contradizem a decisão de mantê-los disponíveis.

## Evidências do código atual

- O modo é resolvido por `servidor/ambiente.py` e consumido por `app.py` e
  `alembic/env.py`.
- `servidor/semente_demo.py` gera vinte perfis genéricos e vinte proxies; os
  proxies têm seis campos e usam `manual_estado="proxy_sintetico"`.
- `Aeronave.extrato_id` é opcional; cada aeronave tem relação com suas fontes
  técnicas. `servidor/catalogo.py` hoje filtra todos os modelos pela versão
  vigente do RAB e restringe sintéticos ao modo DEMO.
- `servidor/importar_rotaer_demo.py` usa sessões distintas e transação, mas
  copia o ROTAER, não os perfis.
- `tests/conftest.py` já aponta para `DATABASE_URL_TESTE`, independente do
  banco do produto.

Não foi feita pesquisa externa nem validação de dados aeronáuticos; isso está
explicitamente fora do escopo aprovado.
