---
title: 'Completar dados didáticos de aeronaves com fontes rastreáveis'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/002-rota-com-escalas/spec.md'
  - '{project-root}/specs/002-rota-com-escalas/plan.md'
  - '{project-root}/specs/002-rota-com-escalas/tasks.md'
  - '{project-root}/_bmad-output/specs/spec-fontes-secundarias-aeronaves/SPEC.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A exigência anterior de POH/AFM oficial para todos os valores impede completar o catálogo quando os manuais não estão disponíveis. O software é exclusivamente didático e precisa de dados rastreáveis sem sugerir aptidão para voo real.

**Approach:** Permitir fontes técnicas oficiais ou secundárias aplicáveis, registrar a procedência de cada campo e priorizar a fonte aplicável mais recente em caso de conflito. Identificar visivelmente valores secundários como estimativas didáticas na seleção, nos resultados e no PDF.

## Boundaries & Constraints

**Always:** Aplicar a mesma regra a todos os modelos, inclusive Cessna 140. Exigir unidade, publicador, referência, data de publicação/revisão e aplicabilidade por valor; registrar também a data de consulta, sem usá-la como substituta da data editorial. Exigir perfil pareado para velocidade e consumo e combustível utilizável. Usar até 30 modelos completos em ordem de frota RAB `CD_INTERDICAO=N`, avião pequeno com PMD aprovado até 5.670 kg e unidade do campo RAB confirmada. Em conflito entre fontes aplicáveis, selecionar a mais recente mesmo se menos específica e registrar as alternativas e a incerteza; em empate temporal, não selecionar nenhuma. Não calcular média. Fonte sem data editorial ou aplicabilidade verificável deixa o campo indisponível. Preservar cálculo no servidor, português e aviso não operacional.

**Never:** Inventar, transferir ou interpolar valores; aceitar modelo incompleto ou fora do limite; apresentar estimativa como oficial, certificada ou adequada a voo real; usar catálogo local como fallback sem RAB vigente; remover valores históricos sem necessidade.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fonte secundária completa | Fonte declara modelo, valor, unidade, publicador, referência, data e perfil aplicável | Modelo elegível se todos os campos obrigatórios estiverem completos; seleção, resultado e PDF identificam a estimativa | Exibir indisponível para qualquer campo ausente |
| Fontes conflitantes | Duas fontes aplicáveis com datas diferentes | Escolher a mais recente mesmo se menos específica e preservar a divergência e incerteza | Nunca calcular média |
| Recência não verificável | Fonte sem data de publicação/revisão, mas com data de consulta | Campo permanece indisponível | A data de consulta não prova quando o conteúdo foi atualizado |

</frozen-after-approval>

## Code Map

- `servidor/modelos.py` -- `Aeronave` guarda valores técnicos escalares e um único `fonte_manual`; precisa de procedência individual por campo.
- `servidor/catalogo.py` -- `modelos_visiveis` aplica completude, ordenação e limite de 30; `carregar_rab` controla frota e associação de modelos.
- `servidor/calculo.py` e `servidor/rota.py` -- cálculos e hipótese de reabastecimento atualmente reutilizam `fonte_manual` para as grandezas.
- `app.py` e `templates/plano_novo.html` -- endpoint e seleção de aeronaves; mostrar rótulo de estimativa e fontes.
- `templates/plano.html` e `servidor/pdf_plano.py` -- resultados e PDF; expor fontes por grandeza e aviso didático.
- `servidor/semente.py` e `alembic/versions/` -- carga reproduzível e migrações; preservar valores antigos sem fonte verificável como inelegíveis.
- `_bmad-output/specs/spec-fontes-secundarias-aeronaves/secondary-sources.md` -- fontes sugeridas pelo usuário; ponto de partida, não comprovação de valores ou aplicabilidade.
- `specs/002-rota-com-escalas/tasks.md` -- execução pendente para confirmar a unidade de PMD no RAB, pesquisar as fontes e implementar a proveniência.
- `tests/test_catalogo_aeronaves.py`, `tests/test_tela_piloto.py`, `tests/test_rota_pdf.py` -- cobrir completude, conflito e identificação de estimativas.

## Tasks & Acceptance

**Execution:**
- [ ] `servidor/catalogo.py`, `specs/002-rota-com-escalas/research.md` -- confirm `NR_PMD` unit in official RAB documentation before applying the 5,670 kg threshold.
- [ ] `tests/test_catalogo_aeronaves.py` -- testar procedência por campo, escolha da fonte mais recente, empate sem seleção e fonte sem data/aplicabilidade.
- [ ] `servidor/modelos.py`, `alembic/versions/` -- persistir referências por campo sem apagar os valores existentes.
- [ ] `servidor/catalogo.py`, `servidor/semente.py` -- validar fontes e oferecer somente os primeiros 30 modelos completos.
- [ ] `app.py`, `servidor/calculo.py`, `servidor/rota.py`, `templates/plano_novo.html`, `templates/plano.html`, `servidor/pdf_plano.py` -- propagar fontes e identificar valores secundários como estimativas didáticas.
- [ ] `documentacao/piloto.md`, `documentacao/operacao.md` -- explicar fontes, estimativas, conflitos e dados indisponíveis.

**Acceptance Criteria:**
- Given campos técnicos completos com fontes aplicáveis, when a seleção é consultada, then só modelos dentro do limite aparecem e cada estimativa secundária está identificada.
- Given fontes aplicáveis conflitantes, when seus valores divergem, then prevalece a fonte mais recente e a divergência fica registrada sem média.
- Given um valor sem data ou aplicabilidade verificável, when a completude é calculada, then o campo fica indisponível e o modelo não é oferecido.
- Given um plano com valores secundários, when a tela e o PDF são exibidos, then mostram fontes por grandeza, o rótulo de estimativa didática e o aviso de que o resultado não serve para voo real nem autoriza voo.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

A fonte precisa ser registrada por campo porque combustível, desempenho e limites podem vir de publicadores diferentes. A prioridade temporal usa a data de publicação/revisão, não a data de consulta.

## Verification

**Commands:**
- `pytest tests/test_catalogo_aeronaves.py tests/test_tela_piloto.py tests/test_rota_pdf.py` -- expected: procedência, conflitos e rótulos didáticos cobertos.
- `pytest` -- expected: suíte completa aprovada.
