---
title: 'Integrar Tailwind CSS ao projeto'
type: 'feature'
created: '2026-11-25'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/_bmad/custom/convivencia-speckit.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O projeto não tem ferramenta de CSS utilitário nem pipeline de estilos; a casca visual é mantida em um bloco `<style>` dentro do template base.

**Approach:** Integrar Tailwind CSS ao processo de assets servido pelo Flask e migrar os estilos atuais da casca para utilitários Tailwind, preservando a aparência e os comportamentos responsivos já aprovados.

**Decisão do piloto:** Migrar os estilos atuais junto com a infraestrutura Tailwind, sem redesenhar as telas.

## Boundaries & Constraints

**Always:** A compilação deve ser reproduzível com dependências travadas, detectar classes nos templates Jinja e produzir CSS que o Flask sirva localmente sem exigir compilação durante cada requisição. Migrar os estilos compartilhados e específicos da casca para utilitários Tailwind, mantendo cores, espaçamentos, tipografia, pontos de quebra e estados visuais atuais. Documentar os comandos de desenvolvimento e build.

**Never:** Adicionar dependências Python, alterar dados ou endpoints, introduzir JavaScript de runtime para CSS ou redesenhar a interface.

</frozen-after-approval>

## Code Map

- `templates/base.html` — contém o CSS compartilhado inline e é herdado pelas páginas; ponto de integração do CSS estático gerado.
- `templates/*.html` — templates Jinja que o compilador precisa escanear para detectar classes utilitárias.
- `static/casca/` — assets estáticos existentes; não há CSS separado nem estrutura de build Node atualmente.
- `tests/test_casca_visual.py` — protege os contratos da casca e pode verificar que a folha gerada é referenciada.
- `documentacao/operacao.md` — explica instalação de dependências e como executar o Flask; deve documentar instalação e build CSS.
- `pyproject.toml` e `uv.lock` — ferramentas Python existentes; manter a cadeia Python e dependências do runtime inalteradas.

## Tasks & Acceptance

**Execution:**
- [ ] `package.json` e lockfile npm — adicionar Tailwind CLI e scripts explícitos de build/watch, com versões reproduzíveis.
- [ ] `static/css/` e `.gitignore` — definir entrada e saída do CSS, fontes Jinja a escanear e ignorar dependências locais; manter o CSS gerado disponível para Flask.
- [ ] `templates/base.html` e demais `templates/*.html` — substituir o CSS inline de apresentação por classes Tailwind, preservar classes semânticas necessárias aos testes e carregar a folha compilada.
- [ ] `tests/test_casca_visual.py` — cobrir a folha gerada, os contratos visuais, breakpoints e a preservação dos estados de espera e navegação.
- [ ] `documentacao/operacao.md` — explicar instalação, build, modo watch e execução do app.

**Acceptance Criteria:**
- Given um checkout limpo com Node/npm instalados, when as dependências frontend são instaladas e o build CSS executado, then Tailwind compila sem erro e produz a folha estática usada pelo Flask.
- Given qualquer template Jinja com classes Tailwind, when o build é executado, then as classes utilizadas aparecem no CSS compilado.
- Given o servidor Flask iniciado sem um processo watcher, when uma página do produto é aberta, then a folha CSS compilada é servida como asset estático.
- Given qualquer tela existente em larguras estreitas e largas, when é renderizada com a folha Tailwind, then a aparência e os comportamentos responsivos da casca aprovada permanecem equivalentes.
- Given o formulário em processamento ou o menu de voo, when as telas correspondentes são abertas, then os estados de espera, bloqueios de navegação e impressão continuam funcionando.

## Implementation Notes

## Verification

**Commands:**
- `npm ci && npm run css:build` — esperado: build reprodutível sem erro.
- `uv run pytest --no-cov tests/test_casca_visual.py` — esperado: testes da casca passam.
- `git diff --check` — esperado: sem erros de whitespace.
- Conferência no navegador em largura móvel e desktop — esperado: casca equivalente à aprovada e sem rolagem horizontal indevida.
