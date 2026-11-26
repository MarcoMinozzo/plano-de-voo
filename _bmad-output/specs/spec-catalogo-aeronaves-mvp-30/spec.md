---
title: 'Limitar o catálogo do MVP a modelos completos'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/002-rota-com-escalas/spec.md'
  - '{project-root}/specs/002-rota-com-escalas/plan.md'
  - '{project-root}/specs/002-rota-com-escalas/tasks.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/EXPERIENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A seleção de aeronaves não garante que os dados estejam completos e associados ao manual oficial da variante exata. Sem um RAB vigente também não é possível provar a ordem de frota do MVP.

**Approach:** Oferecer somente até 30 modelos completos, ordenados pela frota do extrato RAB vigente. Ocultar e recusar modelos sem dados oficiais, fora do limite ou sem associação exata; sem RAB vigente, não oferecer modelos nem aceitar planos novos com aeronave.

## Boundaries & Constraints

**Always:** Voo visual diurno; aplicar a todos os modelos os mesmos critérios de POH/AFM oficial da variante exata, revisão/edição, página/tabela e dados completos: combustível utilizável, velocidade e consumo do mesmo perfil nominal, peso vazio, peso máximo de decolagem e limite de bagagem. Aplicar o limite de 30 depois do filtro de completude e recusar no servidor IDs fora da seleção. Sem RAB vigente, retornar seleção indisponível e vazia. Preservar valores numéricos já registrados, mas não os usar sem comprovação oficial. Manter planos antigos consultáveis e o cálculo de rota existente.

**Never:** Criar regra de elegibilidade por nome de modelo; associar manual por fabricante, PMD, substring ou semelhança; usar fonte secundária para valores de cálculo; completar 30 com dados parciais ou inventados; usar modelo local como fallback do RAB; expor ou aceitar modelos incompletos ou fora da seleção; apagar valores numéricos preexistentes; adicionar dependência ou transferir cálculo ao navegador.

## I/O & Edge-Case Matrix

| Cenário | Entrada / Estado | Comportamento esperado | Tratamento de erro |
|----------|------------------|------------------------|--------------------|
| RAB vigente | Mais de 30 modelos, alguns incompletos | Filtrar completos, ordenar por frota decrescente e nome crescente em empate, retornar até 30 | Nenhum |
| Manual não exato | Fabricante/PMD semelhante, sem variante aplicável confirmada | Modelo fica inelegível; POST/PUT recusam seu identificador | Erro explícito de manual/seleção |
| RAB indisponível | Sem extrato válido | GET retorna indisponível e lista vazia; plano novo é recusado | Não usar cache local como fallback |
| Registro legado não verificado | A fonte não identifica POH/AFM oficial ou variante aplicável | Aplicar o mesmo filtro dos demais modelos e preservar valores gravados | Não calcular até validação oficial |

</frozen-after-approval>

## Code Map

- `servidor/catalogo.py` — `modelos_visiveis` hoje filtra porte e estado, mas não completude nem limite; `_manual_gravado` usa `_compativel_com_manual`, que admite correspondência aproximada. Reutilizar o extrato vigente e eliminar associações heurísticas.
- `servidor/planos.py` — `montar` rejeita manual ausente, mas não verifica se o modelo pertence à seleção atual. Aplicar a mesma elegibilidade para criação e alteração.
- `app.py` — `catalogo_da_tela` descarta o estado do RAB; `/aeronaves` já expõe estado e lista. Propagar o estado para a tela.
- `templates/plano_novo.html` — exibe mensagem genérica quando não há modelos. Preservar o padrão visual e mostrar indisponibilidade/ausência de opções; não permitir envio sem modelo.
- `servidor/modelos.py` — `Aeronave` já contém os campos necessários e `manual_estado`; não ampliar esquema para a regra de seleção.
- `servidor/semente.py` — os dados de semente existentes incluem uma referência “números de estudo”, que não atende a regra oficial. Aplicar a mesma certificação editorial a todos os modelos e preservar valores conforme a constituição.
- `alembic/versions/d4a8c0e21b67_rota_com_escalas.py` — revisão atual do esquema. A migração nova é de dados apenas; atualiza o estado de elegibilidade de registros com fonte não oficial sem apagar valores ou identificar exceções por nome.
- `tests/conftest_rota.py`, `tests/test_catalogo_aeronaves.py`, `tests/test_rota.py` e `tests/test_tela_piloto.py` — fixtures RAB/POH fictícias e cobertura de catálogo, planos e tela. Usar testes, nunca valores técnicos reais.
- `specs/002-rota-com-escalas/` — spec, plano, modelo, contrato e quickstart aprovados para este trabalho; preservar T001–T020 concluídas.
- `EXPERIENCE.md` — o padrão de tela exige mensagem visível para lista vazia e indisponibilidade, sem substituir a identidade visual.

## Tasks & Acceptance

**Execution:**
- [ ] `tests/test_catalogo_aeronaves.py`, `tests/test_rota.py`, `tests/test_tela_piloto.py` — testar corte, completude, correspondência exata, indisponibilidade, recusa POST/PUT e tela vazia.
- [ ] `servidor/catalogo.py` — filtrar completos antes de ordenar e cortar em 30; remover associação aproximada e fallback local.
- [ ] `servidor/planos.py` — recusar em POST/PUT aeronaves fora da seleção vigente.
- [ ] `app.py`, `templates/plano_novo.html` — propagar o estado do RAB e exibir/impedir envio quando não houver opção elegível.
- [ ] `servidor/semente.py`, `alembic/versions/` — aplicar uniformemente o estado sem manual a registros com fonte não oficial, preservando os valores gravados e sem ramificações por nome de modelo.
- [ ] `RAB_EXTRATO`, `servidor/catalogo.py` — carregar extrato vigente e registrar referência identificável sem versionar o arquivo bruto.
- [ ] `servidor/semente.py` — registrar somente os candidatos com POH/AFM oficial completo e citações verificáveis; deixar posições sem comprovação vazias.
- [ ] `documentacao/piloto.md`, `documentacao/operacao.md` — explicar limite, espera, indisponibilidade do RAB e configuração externa do extrato.
- [ ] `specs/002-rota-com-escalas/quickstart.md`, suíte `pytest` — validar cenários vigentes/indisponíveis e regressão.

**Acceptance Criteria:**
- Dado um extrato RAB vigente, quando o piloto abre a seleção, então vê no máximo os 30 primeiros modelos completos após ordenação por frota, com desempate determinístico por nome.
- Dado um modelo incompleto, com manual não aplicável ou fora dos 30, quando seu ID é enviado em POST ou PUT, então o servidor recusa sem gravar plano.
- Dado que o RAB vigente está indisponível, quando a seleção é consultada ou um plano novo é enviado, então a lista fica vazia e indisponível e nenhum modelo local é aceito.
- Dado qualquer registro legado sem POH/AFM verificável, quando a migração roda, então seus valores numéricos permanecem armazenados, o manual fica ausente e os valores não são usados em cálculo.
- Dados planos criados antes da atualização, quando são consultados, então continuam legíveis e pertencem apenas ao piloto proprietário; cálculo, rota, PDF e isolamento não mudam.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Filtrar antes de limitar evita que modelos de maior frota sem documentação ocupem uma das 30 posições. A lista vazia sem RAB é necessária para não afirmar uma ordem que não pode ser verificada. A elegibilidade é uniforme para todos os modelos; a preservação de valores preexistentes não os torna utilizáveis sem fonte oficial.

## Verification

**Commands:**
- `pytest tests/test_catalogo_aeronaves.py tests/test_rota.py tests/test_tela_piloto.py` — os casos novos passam.
- `pytest` — a suíte completa passa.

**Manual checks:**
- Seguir `specs/002-rota-com-escalas/quickstart.md` com extrato vigente e indisponível; confirmar que somente modelos comprovadamente completos aparecem e que a lista vazia não permite envio.
