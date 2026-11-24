# Instruções para o Devin

O projeto se chama Plano de voo. Este texto repete para o Devin a regra do Cursor em `.cursor/rules/speckit-sdd.mdc`. Se as duas divergirem, atualize as duas juntas.

## Spec Kit

A constituição em `.specify/memory/constitution.md` prevalece (versão 2.2.0). As skills oficiais do Devin estão em `.devin/skills/` e as do Cursor em `.cursor/skills/`. Chame cada uma pelo nome, por exemplo `/speckit-specify`. Não reescreva essas skills, nem `.specify/templates/` ou `.specify/scripts/`. Para atualizá-las, use `specify integration upgrade devin`.

A spec ativa é `specs/002-rota-com-escalas/`. `specs/001-planejar-voo-visual/` é o plano direto já construído. O arquivo `.specify/feature.json` fica fora do repositório. Se ele não existir no seu checkout, crie-o com `{"feature_directory":"specs/002-rota-com-escalas"}` antes de chamar uma skill.

Comportamento novo segue esta ordem, um passo por vez:

1. `speckit-constitution` — princípios do projeto; só de novo se um princípio mudar
2. `speckit-specify` — escreve a especificação
3. `speckit-plan` — monta o plano técnico
4. `speckit-tasks` — quebra o plano em tarefas
5. `speckit-implement` — executa só as tarefas ainda desmarcadas, e marque cada uma ao terminar
6. `speckit-converge` — confere o que ainda falta

Antes de editar o servidor, `templates/` ou `static/`, leia a spec indicada em `.specify/feature.json`. Se a mudança não estiver numa tarefa desmarcada, pare e abra a spec. Correção que não muda o que o piloto vê pode ir direto ao código.

## Trabalho em parceria

- Cada passo do Spec Kit vai num pull request próprio, com o artefato gerado na descrição.
- Antes de `speckit-implement`, espere o Marco aprovar a spec, o plano e as tarefas.
- No pull request de implementação, liste as tarefas marcadas e rode `pytest`.
- Dúvida sobre requisito vai para o Marco, ou para `speckit-clarify`. Não invente requisito.

## Regras do produto

O banco do produto é PostgreSQL. Cálculo de voo, PDF, meteorologia, vento, carta e radar ficam no servidor. A interface permanece em português, com unidade e fonte explícitas, e continua avisando que o painel não substitui o manual nem a norma. Fonte sem dado mostra indisponível. Chave de REDEMET e AISWEB fica fora do repositório. Um piloto só vê o próprio plano.

A senha tem no mínimo 8 caracteres. Cinco recusas em 15 minutos bloqueiam a identificação por 15 minutos, com a mesma mensagem de identificação inexistente. A sessão encerra ao sair e após 8 horas sem uso. A orientação do piloto está em `documentacao/piloto.md`. A operação está em `documentacao/operacao.md`, sem segredo.
