---
title: 'Refinamento visual do menu e dos horários'
type: 'feature'
created: '2026-11-26'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/.cursor/rules/speckit-sdd.mdc'
  - '{project-root}/specs/021-redesenho-menu-principal/spec.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O cabeçalho autenticado ainda não apresenta hierarquia, espaçamento e adaptação móvel adequados; os horários do painel exibem precisão desnecessária.

**Approach:** Refinar logo, navegação, ícones, tipografia, cores e menu móvel, mantendo o menu centralizado; exibir os horários em minutos com a indicação “TL”.

</frozen-after-approval>

## Implementation Notes

- O logo autenticado foi ajustado para 140 px; logo e card compartilham o centro vertical, e o menu desktop ajusta a largura ao conteúdo.
- O menu móvel usa `<details>`/`<summary>` e SVGs inline, sem JavaScript ou dependências novas; Sair permanece acessível por nome e visualmente somente ícone.
- Atualizados os tokens existentes para texto `#f2f2f2` e azul translúcido `rgba(8, 42, 84, 0.88)`.
- O painel apresenta a data/hora até minutos e “TL”, sem alterar o valor armazenado.
- Validação: CSS compilado, 8 testes visuais focados aprovados, `git diff --check` sem erros; navegador verificado em 1440 px e 390 px.
