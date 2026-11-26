---
title: 'Filtro integrado na seleção de aeródromos'
type: 'feature'
created: '2026-11-25'
status: 'in-progress'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '/home/mminozzo/plano-de-voo/.specify/memory/constitution.md'
  - '/home/mminozzo/plano-de-voo/_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/EXPERIENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A tela de novo plano mostra filtros separados das caixas de origem e destino. A experiência aprovada prevê que a própria seleção filtre pelo código ou nome do aeródromo, e a tela deve evitar campos redundantes.

**Approach:** Usar um único campo acessível para cada origem e destino: digitar parte do código ou nome filtra opções, e escolher uma opção define o identificador ICAO enviado ao servidor. Preservar valores selecionados ao retornar com erros e não alterar catálogo, validação de domínio ou cálculo da rota.

</frozen-after-approval>

## Implementation Notes

- O mapa de experiência em `EXPERIENCE.md` já especifica um campo de seleção cujo texto filtra pelo código ou nome; `templates/plano_novo.html` atualmente implementa filtros separados e seletores nativos.
- `tests/test_tela_piloto.py` agora verifica a marcação combinada, busca sem acentos, seleção por teclado/clique, rejeição de texto livre e restauração dos valores.
- Mudança de interface somente em `templates/plano_novo.html`; não alterar servidor, catálogo, persistência nem regras de rota.
- Criada a feature Spec Kit `specs/012-filtro-integrado-aerodromos/` antes da alteração do template.
- O seletor aprimora os `<select>` nativos somente quando JavaScript está ativo; a busca é local, parcial e insensível a caixa/acentos, e o formulário continua enviando os ICAOs pelos campos existentes.
- A navegação por setas, Enter, Escape e clique mantém o estado acessível; texto livre é recusado. Sem JavaScript, os seletores nativos permanecem operacionais.
- CSS recompilado com `npm run css:build`. Validação: 19 testes focados passaram e `git diff --check` passou.
