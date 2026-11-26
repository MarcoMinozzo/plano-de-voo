---
title: 'Capa e diagramação técnica do PDF de voo'
type: 'feature'
created: '2026-11-25'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/EXPERIENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O PDF atual é texto corrido, sem capa ou hierarquia visual; fica difícil localizar a rota, os trechos, fontes e avisos.

**Approach:** Adicionar nome de exibição ao perfil e transformar o PDF num relatório técnico legível, com capa da marca, nome, rota e data do voo, seguido de seções bem diagramadas.

## Boundaries & Constraints

**Always:** Exigir nome de exibição aparado, até 160 caracteres, editável pelo próprio piloto; preencher contas existentes com a identificação atual sem alterar login/senha. Manter em português a rota, data/hora, dados, fontes, orientação do piloto e aviso de que o resultado não autoriza o voo. Preservar acesso apenas ao plano do piloto autenticado e usar a identidade visual e biblioteca PDF existentes.

**Never:** Alterar cálculos, dados do plano, checklist, meteorologia ou regras de acesso; omitir procedência, estados indisponíveis, avisos DEMO/sintéticos ou orientação obrigatória; adicionar dependência.

## I/O & Edge-Case Matrix

| Cenário | Entrada / estado | Saída esperada | Tratamento |
|----------|--------------|---------------------------|----------------|
| PDF próprio | Plano, piloto autenticado e data de partida | Capa com logo, nome, rota e data; relatório estruturado | Gerar em memória |
| Relatório longo | Vários trechos, procedência e orientação | Páginas numeradas, sem corte ou sobreposição | Quebra automática |
| Perfil | Cadastro ou edição com nome inválido | Rejeitar sem persistir; nome obrigatório, aparado, até 160 caracteres | Mostrar validação |
| Conta antiga / plano alheio | Perfil legado ou tentativa de outro piloto | Backfill pela identificação; PDF alheio recusado (`404`) | Preservar credenciais |

</frozen-after-approval>

## Code Map

- `servidor/pdf_plano.py:36,112`: gera o conteúdo e hoje desenha texto corrido A4 com quebra por caracteres, incluindo toda a orientação obrigatória.
- `app.py:363` (`pdf`): autentica, verifica propriedade e tem acesso ao piloto atual; passar `nome_exibicao` ao gerador. `servidor/modelos.py:37,187`: adicionar nome ao piloto; plano já guarda rota e partida.
- `servidor/auth.py:39`, `app.py:154`, `templates/cadastro.html`: fluxo atual de conta. `templates/base.html:10` é o menu. Não há edição de perfil; criar tela/rota autenticada.
- Única revisão atual: `d1e2f3a4b5c6`; nova migração deve preenchê-la a partir de `identificacao`, preservando credenciais.
- Reutilizar `static/casca/emblema-plano-de-voo.png`; identidade e checklist vêm de `DESIGN.md` e `EXPERIENCE.md:64` no UX aprovado.
- Ampliar `tests/test_rota_pdf.py`, `tests/test_acesso.py` e `tests/test_casca_visual.py`. `requirements.txt` já fixa ReportLab 4.0.7; não converter HTML em PDF.

## Tasks & Acceptance

**Execution:**
- [ ] `tests/test_acesso.py`, `tests/test_casca_visual.py` e `tests/test_rota_pdf.py` -- cobrir nome, edição própria, migração, capa e paginação -- proteger perfil e documento.
- [ ] `servidor/modelos.py`, `servidor/auth.py` e `alembic/versions/` -- adicionar nome obrigatório e backfill das contas existentes -- manter cadastro e login compatíveis.
- [ ] `app.py`, `templates/cadastro.html`, `templates/base.html` e `templates/perfil.html` -- aceitar nome no cadastro e permitir edição própria -- preservar autenticação atual.
- [ ] `servidor/pdf_plano.py` e `app.py` -- compor capa e relatório com nome, rota, data, seções, tabelas, cabeçalho e numeração -- melhorar leitura sem omitir conteúdo obrigatório.
- [ ] `specs/011-capa-e-diagramacao-pdf/tasks.md` -- detalhar dependências e validar antes do runtime -- seguir o fluxo Spec Kit.

**Acceptance Criteria:**
- Given plano próprio e perfil atualizado, when o piloto solicita o PDF, then a capa exibe emblema, nome atual, rota e data/hora da partida.
- Given cadastro ou edição, when o piloto informa nome válido, then ele é salvo; contas antigas são preenchidas a partir da identificação.
- Given conteúdo extenso ou dados DEMO/indisponíveis, when gera o PDF, then páginas legíveis preservam fontes, avisos e orientação, e checklist não mostra estado marcado.
- Given plano alheio, when solicita PDF, then a aplicação recusa a entrega.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- Capa própria e imprimível: emblema, título, rota, nome, data/hora e aviso. Fundo papel, títulos navy, acento gold, sans-serif; sem blueprint de fundo.
- Organizar resumo, trechos, fontes, meteorologia/vento, checklist e orientação em seções; preservar todo o conteúdo obrigatório atual.
- **Irreversibilidade:** downgrade da migração remove a coluna e perde nomes editados. **Footprint:** perfil, migração, menu, rota e gerador do PDF, testes e tarefa Spec Kit; sem dependências novas.

## Verification

**Commands:**
- `uv run pytest --no-cov tests/test_rota_pdf.py` -- expected: all PDF tests pass.
- `git diff --check` -- expected: no whitespace errors.

**Manual checks:**
- Abrir PDFs de uma rota curta, uma rota com escalas e um caso DEMO. Conferir a capa e páginas seguintes em tela e impressão A4: logo preservado, textos sem corte, contraste, ordem de leitura, fontes, avisos, quebra de páginas e numeração.
