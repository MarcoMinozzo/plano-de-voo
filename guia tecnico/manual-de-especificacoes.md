# Manual de especificações

Guia prático do Plano de voo neste repositório. A constituição vigente é a 2.2.0, em `.specify/memory/constitution.md`. A regra do Cursor que aponta esse fluxo é `.cursor/rules/speckit-sdd.mdc`. As skills ficam em `.cursor/skills/`. Não reescreva as skills, nem `.specify/templates/` nem `.specify/scripts/`.

A spec ativa está em `.specify/feature.json` e hoje é `specs/002-rota-com-escalas`. `specs/001-planejar-voo-visual` é o plano direto já construído. Comportamento novo abre outra pasta em `specs/`.

## 1. Ordem do trabalho

Um passo por vez.

1. `/speckit-constitution` — princípios do projeto. Roda de novo só quando um princípio muda.
2. `/speckit-specify` — escreve a especificação.
3. `/speckit-plan` — monta o plano técnico.
4. `/speckit-tasks` — quebra o plano em tarefas.
5. `/speckit-implement` — executa as tarefas ainda desmarcadas e marca cada uma ao terminar.
6. `/speckit-converge` — compara o código com a spec, o plano e as tarefas, e acrescenta em `tasks.md` o que ainda falta.

Skills opcionais, fora dessa sequência obrigatória:

- `/speckit-clarify` — antes do plano, no máximo cinco perguntas sobre o que a spec deixou vago. As respostas voltam para `spec.md`.
- `/speckit-checklist` — gera uma lista que avalia a qualidade do texto dos requisitos, não se o código funciona.
- `/speckit-analyze` — depois das tarefas e antes de implementar. Só lê `spec.md`, `plan.md` e `tasks.md` e devolve um relatório. Não grava arquivo.
- `/speckit-converge` — depois que `/speckit-implement` já rodou sobre o `tasks.md` atual.

Existe ainda `.cursor/skills/speckit-taskstoissues/SKILL.md`. O próprio texto da skill avisa que `/speckit-taskstoissues` está obsoleto. Este repositório não tem `.specify/extensions.yml`, então a extensão substituta não está instalada. Não use esse comando no fluxo normal.

## 2. Como chamar cada comando no Cursor

A integração deste repositório é `cursor-agent` (`.specify/init-options.json`, Spec Kit 1.2.2). O separador é hífen. Digite a barra e o nome da skill:

| Comando | Skill |
| --- | --- |
| `/speckit-constitution` | `.cursor/skills/speckit-constitution/SKILL.md` |
| `/speckit-specify` | `.cursor/skills/speckit-specify/SKILL.md` |
| `/speckit-plan` | `.cursor/skills/speckit-plan/SKILL.md` |
| `/speckit-tasks` | `.cursor/skills/speckit-tasks/SKILL.md` |
| `/speckit-implement` | `.cursor/skills/speckit-implement/SKILL.md` |
| `/speckit-converge` | `.cursor/skills/speckit-converge/SKILL.md` |
| `/speckit-clarify` | `.cursor/skills/speckit-clarify/SKILL.md` |
| `/speckit-checklist` | `.cursor/skills/speckit-checklist/SKILL.md` |
| `/speckit-analyze` | `.cursor/skills/speckit-analyze/SKILL.md` |

O texto depois do comando é o argumento. Em `/speckit-specify`, esse texto é a descrição da feature. Se vier vazio, a skill para com erro.

## 3. Entrada e saída de cada comando

| Comando | O que informar | O que produz |
| --- | --- | --- |
| `/speckit-constitution` | O princípio ou a seção que muda | Só `.specify/memory/constitution.md`. Não mexe em código nem em `specs/`. |
| `/speckit-specify` | Descrição em linguagem natural, uma feature por chamada | `specs/<número>-<nome>/spec.md`, `checklists/requirements.md` e a pasta ativa em `.specify/feature.json`. |
| `/speckit-clarify` | Opcional. Sem descrição, a skill lê a spec ativa | Atualiza `spec.md` e, se existir, `checklists/requirements.md`. Não cria spec nova. |
| `/speckit-plan` | Detalhe técnico, se houver. Lê a spec ativa | `plan.md`, `research.md`, `data-model.md`, `contracts/` e `quickstart.md` na pasta da feature. |
| `/speckit-tasks` | Nada obrigatório. Lê spec, plano e, se existirem, modelo, contratos, pesquisa e quickstart | `tasks.md`, com tarefas no formato `- [ ] T001 ...`. |
| `/speckit-checklist` | O tema da lista (segurança, revisão, e assim por diante) | Um arquivo novo ou um acréscimo em `specs/<feature>/checklists/`, com nome curto. Não marca os itens como feitos. |
| `/speckit-analyze` | Nada obrigatório. Exige spec, plano e tarefas | Relatório no chat. Não altera arquivo. |
| `/speckit-implement` | Nada obrigatório. Lê as tarefas desmarcadas | Código, testes e documentação citados nas tarefas. Marca cada tarefa concluída com `[X]`. |
| `/speckit-converge` | Nada obrigatório | Se faltar algo, acrescenta uma fase no fim de `tasks.md`. Não altera `spec.md` nem `plan.md`. |

Os modelos de página estão em `.specify/templates/`: `constitution-template.md`, `spec-template.md`, `plan-template.md`, `tasks-template.md` e `checklist-template.md`. Os scripts que localizam a feature ativa estão em `.specify/scripts/bash/`: `setup-plan.sh`, `setup-tasks.sh` e `check-prerequisites.sh`.

`checklists/requirements.md` é a lista de qualidade da spec, mantida por `/speckit-specify` e `/speckit-clarify`. `/speckit-implement` trata essa pasta como portão: se algum item estiver desmarcado, a skill para e pergunta se deve continuar. Nas duas specs atuais essa lista está toda marcada.

## 4. Abrir uma spec nova

`/speckit-specify` cria uma pasta por chamada. A numeração deste repositório é `sequential` (`.specify/init-options.json`). O prefixo é o próximo número de três dígitos que ainda não existe em `specs/`. O nome curto sai da descrição.

Hoje existem `001-planejar-voo-visual` e `002-rota-com-escalas`. A próxima pasta, se a descrição pedisse autenticação de usuário, seria algo como `specs/003-user-auth`. O nome da pasta e o nome do branch git são independentes.

A skill grava a pasta escolhida em `.specify/feature.json`:

```json
{
  "feature_directory": "specs/003-user-auth"
}
```

Os comandos seguintes leem esse arquivo. Não descreva a feature dentro dos templates nem dos scripts.

Antes de editar `servidor/`, `templates/` ou `static/`, leia a spec apontada por `.specify/feature.json`. Se a mudança não estiver numa tarefa ainda desmarcada, pare e abra a spec. Correção que não muda o que o piloto vê pode ir direto ao código.

## 5. Constituição e mudança de princípio

A constituição prevalece sobre conveniência de implementação. Os cinco princípios atuais são: especificação antes do código, limite educacional, cálculo no servidor, unidades e fonte explícitas, pilha pequena e banco relacional. Em seguida vêm segurança do acesso, catálogo nacional e rota, e a pilha nomeada (Python 3.10+, Flask 3.0.0, PostgreSQL 16, SQLAlchemy 2, psycopg 3, Alembic, Leaflet 1.9 pelo CDN, pytest).

Quando um princípio muda, rode `/speckit-constitution`. A versão sobe assim:

- MAJOR remove ou redefine um princípio.
- MINOR acrescenta princípio ou seção.
- PATCH só esclarece texto.

A linha de versão fica no fim do arquivo. A atual é `2.2.0`, ratificada e emendada em 2026-10-21. A skill também pede um comentário HTML no topo com o relatório da emenda. Esse comentário é rascunho de revisão e deve sair antes do commit da emenda.

Spec, plano e tarefas novos têm de caber na constituição. `/speckit-analyze` trata conflito com a constituição como achado crítico. Comportamento que o piloto vê e que ainda não está numa spec começa em `/speckit-specify`, não no código.

## 6. Implementar e testar

`/speckit-implement` percorre `tasks.md` da spec ativa, fase por fase, e marca `[X]` ao terminar. Se `tasks.md` não existir, rode antes `/speckit-tasks`.

Para conferir o que já está no repositório, na raiz, com o `.venv` ativo e o PostgreSQL 16 em execução:

```bash
pip install -r requirements.txt
alembic upgrade head
python -m servidor.semente
flask --app app:criar_app run
```

Os valores ficam em `.env`, copiado de `.env.example`. Não grave senha nem chave em `documentacao/operacao.md`. `DATABASE_URL` é a base de desenvolvimento. `DATABASE_URL_TESTE` é só dos testes.

Os testes estão em `tests/` (`test_calculo.py`, `test_acesso.py`, `test_isolamento.py`, `test_tempo.py`, `test_pdf.py`, `test_historico.py`, `test_orientacao.py`, `test_operacao_doc.py`). `pytest.ini` define `pythonpath = .`. Com `DATABASE_URL_TESTE` definido:

```bash
.venv/bin/pytest
```

A constituição pede pytest para cálculo, limite do manual e isolamento entre pilotos, e uma conferência manual no navegador. O roteiro dessa conferência é o `quickstart.md` da feature.

## 7. A pasta `guia tecnico`

`guia tecnico/` guarda material de consulta. Não é spec, não é constituição e não entra no fluxo `/speckit-*`.

- `rfc2119.txt` é a RFC 2119. A constituição usa MUST e MAY nesse sentido: obrigação e permissão.
- `diretos-de-especificacao.md` descreve, arquivo por arquivo, `.specify/`, `specs/` e `.cursor/`.
- Os demais arquivos são referências públicas sobre ASD-STE100 (Simplified Technical English), não a norma em si. A cópia oficial da especificação só sai pelo formulário de pedido em asd-ste100.org e não está nesta pasta.

Arquivos de referência já gravados:

- `whitepaper-asd-ste100-e-ia.pdf` — white paper da STEMG sobre STE e inteligência artificial.
- `asd-europa-faq-ste.html`, `asd-europa-bases-do-ste.html`, `asd-europa-issue-9.html` — páginas públicas da ASD Europa.
- `istc-unwalla-simplified-technical-english.pdf` — slides do ISTC.
- `techscribe-asd-ste100.html` e os três PDFs `techscribe-*` — artigos públicos da TechScribe.
- `kuhn-controlled-natural-languages.pdf` — levantamento de linguagens controladas, com uma seção sobre o ASD-STE.

A orientação que o piloto lê continua em `documentacao/piloto.md`. A operação continua em `documentacao/operacao.md`.

## 8. Glossário

**Spec.** `spec.md` da feature. Diz o que o piloto precisa, sem escolher biblioteca. Exemplos: `specs/001-planejar-voo-visual/spec.md` e `specs/002-rota-com-escalas/spec.md`.

**Plan.** `plan.md`. Traduz a spec para a pilha deste repositório e aponta `research.md`, `data-model.md`, `contracts/` e `quickstart.md`.

**Tasks.** `tasks.md`. Lista ordenada do que implementar. Cada linha começa com `- [ ]` ou `- [X]`, um identificador `T001` e o arquivo a mexer.

**Constituição.** `.specify/memory/constitution.md`. Regras que spec, plano e código não podem contrariar. Versão atual: 2.2.0.

**Skill.** Arquivo `SKILL.md` em `.cursor/skills/speckit-*`. É o texto que o Cursor segue quando você digita o comando com barra.

**Template.** Modelo em `.specify/templates/`. O comando copia a estrutura; a feature fica em `specs/`, não no modelo.

**ROTAER.** Publicação Auxiliar de Rotas Aéreas, do DECEA. Na constituição, o catálogo de aeródromos vem da emenda vigente, pela área `rotaer` do AISWEB. Sem essa emenda, o catálogo nacional fica indisponível.

**WAC.** Carta Aeronáutica Mundial, escala 1:1.000.000, publicada no AISWEB. Na constituição, a carta visual vigente do plano é a WAC cuja área cobre a rota. Sem a chave do AISWEB, a carta fica indisponível.

**CDN.** Rede que entrega o arquivo ao navegador. Aqui só o mapa: Leaflet 1.9, carregado pelo CDN. O cálculo não vai para o JavaScript.

**JWT e sessão.** Este projeto não usa JWT. O acesso do piloto é hash de senha do Werkzeug e sessão do Flask, sem segundo fator. `SECRET_KEY` assina essa sessão. O cookie é HttpOnly e SameSite=Lax, e Secure fora de acesso local. A sessão encerra ao sair e após 8 horas sem uso.
