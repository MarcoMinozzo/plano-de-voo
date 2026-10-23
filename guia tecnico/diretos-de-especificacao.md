# Diretórios de especificação

Este texto descreve os arquivos de especificação que estão neste repositório. O projeto se chama Plano de voo. A versão do Spec Kit registrada na inicialização é 1.2.2, com a integração `cursor-agent`.

## `.specify/`

Pasta do Spec Kit neste projeto. Guarda a constituição, os modelos em branco, os scripts que as skills chamam, o fluxo automático e o registro da integração instalada.

### `feature.json`

Aponta a feature ativa. O valor gravado é `specs/002-rota-com-escalas`. O `.gitignore` desta pasta diz que o arquivo é reescrito a cada troca de feature e não deve ser compartilhado.

### `.gitignore`

Lista o que o Spec Kit trata como estado local: `feature.json`, `extensions/*/local-config.yml`, `integrations/packages/` e `integrations/packages.json`. O comentário do arquivo diz que o CLI preserva edições deste ignore numa atualização.

### `init-options.json`

Grava as opções usadas em `specify init`: integração `cursor-agent`, skills de agente ligadas, numeração de feature `sequential`, script `sh`, versão `1.2.2`, `here` verdadeiro e `allow_symlinks` falso.

### `integration.json`

Registra a integração instalada. A única entrada é `cursor-agent`, também marcada como padrão. O separador de invocação é `-`, então os comandos saem como `speckit-specify` e não com ponto. O script associado é `sh`. A versão registrada é 1.2.2.

### `integrations/cursor-agent.manifest.json`

Manifesto da integração Cursor. Lista os dez arquivos `.cursor/skills/speckit-*/SKILL.md` instalados em 2026-10-21, cada um com o hash do conteúdo naquela instalação.

### `integrations/speckit.manifest.json`

Manifesto dos arquivos do próprio Spec Kit copiados para o projeto: os seis scripts em `scripts/bash/`, os cinco modelos em `templates/` e o `.gitignore`. Cada caminho tem um hash. A versão registrada é 1.2.2.

### `memory/constitution.md`

Constituição do projeto, versão 2.2.0, ratificada e emendada em 2026-10-21. Define os princípios que o agente deve seguir: especificação antes do código, limite educacional, cálculo no servidor, unidade e fonte, pilha Flask com PostgreSQL. A seção «Catálogo nacional e rota» exige os aeródromos de avião da emenda vigente do ROTAER, os modelos de avião pequeno do registro público e a escolha da rota com escalas no servidor. O comentário no topo é o relatório da emenda 2.1.1 para 2.2.0. A spec ativa nomeada no texto é `specs/002-rota-com-escalas/`.

### `memory/.constitution-template.json`

Proveniência do modelo de constituição materializado na inicialização. Guarda o hash SHA-256 do conteúdo e a fonte `core`. Não é o texto da constituição.

### `scripts/bash/common.sh`

Funções compartilhadas pelos outros scripts. A primeira localiza a raiz do repositório subindo diretórios até achar `.specify`.

### `scripts/bash/check-prerequisites.sh`

Confere se a feature ativa tem os artefatos pedidos. Aceita `--json`, `--require-spec`, `--require-tasks`, `--include-tasks`, `--paths-only` e `--template`. Em JSON devolve `FEATURE_DIR` e `AVAILABLE_DOCS`.

### `scripts/bash/create-new-feature.sh`

Cria o diretório da feature em `specs/`. Calcula o próximo número a partir das pastas já existentes, monta o nome curto e aplica o limite de 244 bytes do nome de branch do GitHub. Aceita descrição, número explícito e `--json`.

### `scripts/bash/resolve-template.sh`

Resolve um modelo pelo nome. O uso impresso pelo próprio script é `resolve-template.sh <template-name> [--json]`. As skills de constituição e de plano chamam este script para obter o modelo vigente, em vez de ler só a cópia em `templates/`.

### `scripts/bash/setup-plan.sh`

Prepara o plano da feature ativa. Garante que o diretório da feature existe e copia o modelo de plano se `plan.md` ainda não existir. Com `--json`, imprime os caminhos.

### `scripts/bash/setup-tasks.sh`

Prepara `tasks.md`. Exige os arquivos obrigatórios da feature, monta a lista de documentos disponíveis e resolve o modelo de tarefas pela pilha de override. Com `--json`, devolve o modelo e essa lista.

### `templates/constitution-template.md`

Modelo em branco da constituição. Traz o título `[PROJECT_NAME] Constitution`, cinco princípios com placeholder e as seções de governança ainda sem texto do projeto. A constituição preenchida fica em `memory/constitution.md`, não neste arquivo.

### `templates/spec-template.md`

Modelo de `spec.md`. Obriga histórias de usuário com prioridade e teste independente, requisitos funcionais, critérios de sucesso e premissas. O campo de entrada é `$ARGUMENTS`.

### `templates/plan-template.md`

Modelo de `plan.md`. As seções são Summary, Technical Context, Constitution Check, Project Structure e Complexity Tracking. O Constitution Check fica para ser preenchido a partir da constituição, não com uma cópia fixa dela.

### `templates/tasks-template.md`

Modelo de `tasks.md`. Define o formato `[ID] [P?] [Story]`, fases de setup, fundação, uma fase por história e polish, mais a ordem de dependência. Os itens de exemplo continuam genéricos.

### `templates/checklist-template.md`

Modelo de checklist. O cabeçalho diz que o comando `/speckit-checklist` substitui os itens de exemplo pelos critérios da feature, e que `[x]` significa critério de qualidade revisado, não tarefa de implementação concluída.

### `workflows/workflow-registry.json`

Registro dos fluxos instalados. O único fluxo é `speckit`, nome «Full SDD Cycle», versão 1.0.1, origem `bundled`, descrito como specify, plan, tasks e implement com portões de revisão. As datas de instalação são 2026-10-21.

### `workflows/speckit/workflow.yml`

Definição desse fluxo. Exige Spec Kit `>=0.8.5`. A entrada obrigatória é o texto `spec`. Os passos são `speckit.specify`, um portão que aborta se a spec for rejeitada, `speckit.plan`, outro portão, `speckit.tasks` e `speckit.implement`. A integração padrão da entrada é `auto`.

### `extensions/.cache/`

Cache do catálogo de extensões. `catalog-metadata.json` e `catalog.json` apontam para `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json`, com `cached_at` em 2026-10-21. Há ainda a cópia `catalog-ebf165086500aab1.json` e o metadata correspondente.

### `presets/.cache/`

Cache do catálogo de presets, no mesmo formato. A URL gravada é `https://raw.githubusercontent.com/github/spec-kit/main/presets/catalog.json`. Os arquivos são `catalog.json`, `catalog-metadata.json`, `catalog-ff86b51b80a289e5.json` e o metadata desse hash.

## `specs/`

Artefatos das features. `specs/.gitkeep` está vazio e só mantém a pasta sob controle de versão quando não há outro arquivo.

### `001-planejar-voo-visual/`

Feature do plano direto, criada em 2026-10-21. O texto de abertura dos outros arquivos desta pasta remete o catálogo nacional e as escalas para `002-rota-com-escalas`.

`spec.md` descreve o plano de voo visual: origem, destino e hora, manual da aeronave, dados particulares, tempo, carta, radar, vento, checklist, PDF, acesso sem segundo fator e histórico. Os requisitos vão de FR-001 a FR-024. As premissas dizem que os sete aeródromos e o manual do Cessna 140 são o escopo deste documento.

`plan.md` fixa a pilha já usada: Flask 3.0.0, PostgreSQL 16, SQLAlchemy 2, psycopg 3, Alembic, requests 2.31.0, reportlab 4.0.7 e Leaflet 1.9. O Constitution Check está preenchido. A árvore de código aponta `servidor/`, `templates/` e `documentacao/`.

`research.md` registra as decisões desse plano: PostgreSQL no lugar de SQLite, METAR e TAF do Aviation Weather Center, radar MaxCappi da REDEMET, carta WAC do AISWEB, vento de área da REDEMET e sessão com hash do Werkzeug.

`data-model.md` descreve piloto, tentativa de entrada, aeronave, aeródromo, plano e item de checklist, com as regras de senha, peso e origem diferente do destino.

`quickstart.md` é o roteiro manual depois da implementação: migração, semente, cadastro, plano SBJD para SBAU, PDF, segundo piloto e saída.

`tasks.md` lista T001 a T040. T001 a T036 estão marcadas. T037 a T040, na Phase 11, continuam abertas: retirar `templates/index.html`, ler o vento de área, mostrar METAR e TAF, e escolher a WAC da região.

`checklists/requirements.md` é o checklist de qualidade da spec. Os itens estão marcados. A nota diz que cookie e banco ficaram no plano e na constituição, não na spec.

`contracts/api-plano.md` descreve cadastro, entrada, saída e as rotas de plano. Plano de outro piloto recebe a mesma recusa, sem revelar se o plano existe.

### `002-rota-com-escalas/`

Feature do catálogo nacional e da rota com escalas, também de 2026-10-21. É a spec nomeada como ativa na constituição e na regra do Cursor.

`spec.md` pede todos os aeródromos de avião da emenda vigente, os modelos de avião pequeno do registro público ordenados pela frota, e a rota de menor tempo com as escalas necessárias. A reserva citada é a de 30 minutos do voo visual diurno. Heliponto, número inventado e protocolo do plano ficam de fora.

`plan.md` mantém a mesma pilha e diz que não há biblioteca nova. O desenho acrescenta `servidor/catalogo.py` e `servidor/rota.py`. O Constitution Check cobre emenda vigente e manual ausente.

`research.md` nomeia a área `rotaer` do AISWEB, o extrato público do Registro Aeronáutico Brasileiro, o RBAC nº 01 para o porte de 5.670 kg, o RBAC nº 91.151 para a reserva e a área `sol` do AISWEB para o pôr do sol.

`data-model.md` acrescenta emenda do ROTAER, tipo do aeródromo, extrato do RAB, estado do manual e trechos ordenados do plano. Os sete indicativos antigos podem permanecer, mas não contam como catálogo nacional.

`quickstart.md` descreve a conferência da carga real e de dois pares: um direto que cabe na reserva e um que exige escala. Sem a chave do AISWEB, o resultado esperado é catálogo indisponível.

`tasks.md` lista T001 a T020, todas desmarcadas. A ordem é migração, catálogo de aeródromos, catálogo de aviões, escolha da rota, tela e PDF.

`checklists/requirements.md` marca os 16 critérios de qualidade da spec. A nota registra que o corte de 80% da frota está no FR-004 e nas premissas.

`contracts/api-rota.md` descreve `GET /aerodromos`, `GET /aeronaves` e o acréscimo de `rota` em `POST /planos` e `PUT /planos/{id}`. Não há campo de escala na entrada.

## `.cursor/`

Arquivos que o Cursor lê. Nesta árvore só há a regra do Spec Kit e as skills geradas pela integração `cursor-agent`.

### `rules/speckit-sdd.mdc`

Regra com `alwaysApply: true`. Diz que a constituição 2.2.0 prevalece, que as skills oficiais estão em `.cursor/skills/` e que não se reescreve skill, modelo nem script para descrever uma feature. A spec ativa indicada é `specs/002-rota-com-escalas/`. A ordem escrita é constitution, specify, plan, tasks, implement e converge. Antes de editar o servidor ou `templates/`, a regra manda ler `.specify/feature.json` e parar se a mudança não estiver numa tarefa desmarcada.

### Skills

Cada skill é um `SKILL.md` com o texto do comando correspondente do Spec Kit. O campo `source` do frontmatter aponta o modelo de comando de origem. Nenhuma delas altera o comportamento sozinha: o agente as segue quando o comando é invocado.

`skills/speckit-constitution/SKILL.md` cria ou atualiza `.specify/memory/constitution.md` a partir dos princípios informados. Não altera código de aplicação. A versão sobe conforme a emenda seja major, minor ou patch.

`skills/speckit-specify/SKILL.md` cria uma pasta nova em `specs/` a partir da descrição da feature, grava `spec.md` com o modelo e o checklist de qualidade, e atualiza `feature.json`. Uma invocação cria uma feature.

`skills/speckit-clarify/SKILL.md` procura trechos subespecificados na spec ativa e faz até cinco perguntas. As respostas voltam para a spec.

`skills/speckit-plan/SKILL.md` gera `plan.md`, `research.md`, `data-model.md`, `contracts/` e `quickstart.md` da feature ativa. O Constitution Check é preenchido com a constituição vigente.

`skills/speckit-tasks/SKILL.md` gera `tasks.md` em fases, uma história por fase, com identificadores e dependências, a partir do plano e da spec.

`skills/speckit-checklist/SKILL.md` gera um checklist próprio da feature a partir do pedido de quem chama. Não marca implementação como pronta.

`skills/speckit-analyze/SKILL.md` compara `spec.md`, `plan.md` e `tasks.md` sem gravar nesses arquivos. Conflito com a constituição é tratado como crítico.

`skills/speckit-implement/SKILL.md` executa as tarefas ainda desmarcadas em `tasks.md`, na ordem das fases, e marca cada uma ao terminar.

`skills/speckit-converge/SKILL.md` compara o código com a spec, o plano e as tarefas. Se houver lacuna, só acrescenta uma fase nova no fim de `tasks.md`. Se não houver, não altera o arquivo.

`skills/speckit-taskstoissues/SKILL.md` está marcada como obsoleta no próprio frontmatter. O texto ainda descreve a conversão das tarefas da feature em issues do GitHub.

## `README.md` e `documentacao/`

`README.md` nomeia o projeto como Plano de voo, aponta `documentacao/operacao.md` para subir o serviço e `documentacao/piloto.md` para o texto do piloto. Também aponta as duas pastas de spec.

`documentacao/piloto.md` é o texto que a tela do plano e o PDF leem. Explica o que o piloto informa, o que significa um item indisponível e que o resultado não autoriza o voo.

`documentacao/operacao.md` traz os comandos de instalação, migração, semente e subida do Flask, e a tabela de nomes de variáveis de ambiente, sem valores. A seção «Catálogo nacional» diz que a carga do ROTAER e do registro de aeronaves está especificada em `specs/002-rota-com-escalas/` e que o comando dessa carga ainda não está neste texto.

## Como as pastas se relacionam

`.specify/memory/constitution.md` governa o projeto. `.specify/templates/` e `.specify/scripts/bash/` são o maquinário que as skills usam. As skills em `.cursor/skills/` ordenam o trabalho: `speckit-specify` abre a pasta em `specs/`, `speckit-plan` e `speckit-tasks` completam essa pasta, e `speckit-implement` só executa tarefa desmarcada. A regra `.cursor/rules/speckit-sdd.mdc` aponta a constituição, a spec ativa e essa ordem. `specs/` guarda o contrato de cada feature; `documentacao/` guarda o texto que o piloto e quem opera leem.
