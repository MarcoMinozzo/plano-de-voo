---
title: 'Restaurar a lista das 20 aeronaves de teste'
type: 'bugfix'
created: '2026-11-26'
status: 'draft'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/015-banco-unico-sem-demo/spec.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A seleção de aeronaves no novo plano está vazia porque a base canônica não contém perfis sintéticos selecionáveis. Os vinte valores sintéticos antigos existem apenas como perfis genéricos numerados.

**Approach:** Importar os valores existentes para os vinte modelos de teste já definidos, relacionando os perfis `01` a `20` pela ordem da lista estabelecida. Cada opção mostra somente o nome correto do modelo. O fim do card de entrada e o fim do relatório PDF apresentam os avisos sobre cálculos e dados didáticos: não validados, sem representar o modelo, sem substituir manual, treinamento ou norma, e sem autorizar voo real.

## Boundaries & Constraints

**Always:** Usar a base de produto já configurada; ler a origem legada sem modificá-la; fazer backup do destino antes da importação; preservar os seis valores e unidades existentes por perfil; manter a importação transacional e idempotente; manter a identificação dos dados sintéticos e os avisos de segurança no fim do card de entrada e do relatório PDF.

**Never:** Criar outra base de produto; gerar ou recalcular valores; importar pilotos, planos, aeródromos ou perfis genéricos com seus nomes; alterar os registros factuais do RAB; exibir `DEMO` ou `sintético` no nome da opção; apagar ou migrar o esquema da origem.

## I/O & Edge-Case Matrix

| Cenário | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Importação válida | Vinte perfis genéricos completos na origem | Vinte opções com os nomes corretos dos modelos e valores/unidades preservados no produto | Nenhum |
| Origem incompleta ou divergente | Perfil, campo ou unidade ausente; conflito no destino | Nenhuma gravação parcial; origem e registros existentes permanecem intactos | Erro explícito identificando o problema |
| Repetição | Os vinte perfis já foram importados sem divergências | Nenhuma duplicata ou alteração; lista continua com vinte modelos | Conflitos interrompem a transação |

</frozen-after-approval>

## Code Map

- `servidor/importar_perfis_sinteticos.py` -- importador atual espera estado e nomes de proxy que não correspondem à origem disponível, que está na revisão `c8d3f41a2b67`.
- `servidor/perfis_sinteticos.py` -- define a ordem dos vinte modelos e atualmente prefixa o nome de exibição.
- `servidor/catalogo.py` -- inclui perfis sintéticos na lista quando os registros correspondem aos nomes definidos.
- `templates/plano_novo.html` -- mostra os nomes das opções e a nota separada da lista.
- `tests/test_importar_perfis_sinteticos.py`, `tests/test_perfis_sinteticos.py` e `tests/test_tela_piloto.py` -- cobrem importação, ordenação dos perfis e apresentação.
- `documentacao/operacao.md` -- documenta a importação única, backup e uso de uma única base de produto.

## Tasks & Acceptance

**Execution:**
- [ ] `servidor/importar_perfis_sinteticos.py`, `tests/test_importar_perfis_sinteticos.py` -- ler a origem antiga em modo somente leitura, associar cada perfil numerado ao modelo correspondente pela ordem definida e preservar os seis valores/unidades, com transação, idempotência e falha sem gravação parcial.
- [ ] `servidor/perfis_sinteticos.py`, `templates/plano_novo.html`, `templates/plano.html`, `servidor/pdf_plano.py`, `tests/test_perfis_sinteticos.py`, `tests/test_tela_piloto.py`, `tests/test_rota_pdf.py` -- mostrar apenas os nomes corretos dos vinte modelos e apresentar os avisos sintéticos no fim do card de entrada e do relatório PDF.
- [ ] Base de produto configurada -- fazer backup, importar os vinte perfis existentes e verificar que `/aeronaves` e `/planos/novo` os apresentam sem duplicatas.

**Acceptance Criteria:**
- Given a origem com vinte perfis sintéticos completos, when a importação termina, then a base de produto contém exatamente os vinte perfis associados aos modelos já definidos, com todos os seis valores e unidades preservados.
- Given a tela de novo plano, when a lista é exibida, then as opções mostram somente os nomes corretos dos modelos e o aviso sobre os valores didáticos aparece no fim do card.
- Given um plano com perfil sintético, when o PDF é aberto, then os valores aparecem identificados como sintéticos e o aviso didático fica no fim do relatório.
- Given uma origem incompleta, conflito ou repetição, when a importação ocorre, then não há gravação parcial, sobrescrita ou duplicação.
- Given a base de produto única, when aplicação e Alembic operam, then ambos continuam usando a mesma `DATABASE_URL`.

## Implementation Notes

Diagnóstico somente de leitura: `/planos/novo` responde HTTP 200; a base de produto tem 2.143 aeronaves, todas com `manual_estado='ausente'`, e nenhum perfil sintético. A origem local na porta 55432 tem vinte registros `Aeronave DEMO 01–20`, com seis fontes sintéticas selecionadas cada; os metadados antigos não associam os números a modelos, então a correspondência segue a ordem estável de `PERFIS_SINTETICOS`. A origem está na revisão `c8d3f41a2b67` e não será alterada.

## Spec Change Log

## Review Triage Log

## Design Notes

A aplicação permanece conectada apenas à base canônica após a importação. O nome da opção não carregará rótulos de demonstração. O aviso ao fim do card e do PDF atende à identificação exigida sem poluir os nomes dos vinte modelos.

## Verification

**Commands:**
- `uv run pytest tests/test_importar_perfis_sinteticos.py tests/test_perfis_sinteticos.py tests/test_tela_piloto.py` -- esperado: importação idempotente, nomes limpos e lista de vinte perfis.

**Manual checks:**
- Conferir backup antes da escrita, confirmar vinte resultados no endpoint/tela e que a origem permaneceu inalterada.
