# Convivência com o Spec Kit

Este repositório já entrega o Plano de voo pelo Spec Kit. A constituição em `.specify/memory/constitution.md` prevalece.

- Spec do produto: `specs/<feature>/spec.md`, `plan.md` e `tasks.md`, pelas skills `speckit-*` em `.cursor/skills/`.
- Spec do BMAD: `_bmad-output/specs/spec-<slug>/`. Não grave spec do BMAD em `specs/`.
- Não altere `.specify/`, `.cursor/skills/speckit-*` nem `.cursor/rules/speckit-sdd.mdc`.
- Brief, PRD, arquitetura e elicitação do BMAD preparam a mudança. Comportamento que o piloto vê só entra no código depois de uma tarefa desmarcada em `specs/`.
- `bmad-build` não edita `servidor/`, `templates/` nem `static/` para mudança observável. Correção sem mudança observável pode ir direto ao código.
- Documentação do piloto e da operação fica em `documentacao/`, não numa pasta `docs/` paralela.
