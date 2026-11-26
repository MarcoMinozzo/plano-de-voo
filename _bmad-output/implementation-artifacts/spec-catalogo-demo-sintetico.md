---
title: 'Catálogo sintético isolado para DEMO'
type: 'feature'
created: '2026-11-24'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/.cursor/rules/speckit-sdd.mdc'
  - '{project-root}/specs/006-catalogo-demo-sintetico/spec.md'
  - '{project-root}/specs/002-rota-com-escalas/spec.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O catálogo precisa de valores técnicos para destravar o desenvolvimento, mas ainda não há fontes verificadas suficientes para completar vinte aeronaves reais. Inventar valores associados a modelos reais violaria as regras do produto.

**Approach:** Disponibilizar vinte perfis fictícios, identificados como sintéticos, em um modo DEMO isolado e impossível de iniciar em produção. A seleção e os cálculos devem manter a procedência sintética e o aviso não operacional; o catálogo normal continua aceitando apenas fontes rastreáveis.

## Boundaries & Constraints

**Always:** Usar nomes genéricos, como “Aeronave DEMO 01”; rotular os dados em toda superfície que os apresente; usar armazenamento DEMO exclusivo, sem fallback; rejeitar o modo DEMO em produção; manter o cálculo no servidor e a interface em português; preservar as alterações existentes no worktree; não permitir que o modo normal selecione ou calcule perfis sintéticos; permitir planos de rota no DEMO somente quando houver uma emenda oficial vigente do ROTAER carregada no armazenamento DEMO.

**Never:** Associar valores sintéticos a marcas ou modelos reais; gravar ou consultar dados sintéticos no armazenamento de produção; inventar coordenadas, vento, meteorologia, carta ou pôr do sol; apresentar o resultado como apto para planejamento de voo real ou como autorização.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| DEMO configurado | Ambiente não produtivo e armazenamento DEMO exclusivo | Catálogo expõe vinte perfis com valores, unidades e rótulo sintético | Nenhum fallback para o armazenamento normal |
| DEMO em produção | Solicitação de ativar o modo DEMO | Inicialização recusada antes de abrir ou alterar dados | Erro explícito de configuração |
| DEMO sem armazenamento isolado | URL ausente, inválida ou igual à URL normal | Inicialização recusada | Erro explícito; não usar armazenamento normal |
| Perfil sintético no modo normal | Registro sintético presente no banco normal | Perfil não aparece e não passa na validação de cálculo | Recusar explicitamente o uso |
| Carga repetida | Os vinte perfis já existem no armazenamento DEMO | Catálogo mantém exatamente vinte perfis | Não duplicar nem apagar registros |

</frozen-after-approval>

## Code Map

- `app.py` -- `criar_app` lê apenas `DATABASE_URL`; `/aeronaves` e `catalogo_da_tela` consultam o catálogo sem contexto DEMO.
- `servidor/modelos.py` -- `Aeronave.estimativa_didatica` reconhece somente fontes secundárias; `FonteTecnicaAeronave.data_publicacao` é obrigatória.
- `servidor/proveniencia.py` -- `selecionar_fonte_aplicavel`, `procedencia_aeronave` e `modelo_tecnicamente_completo` permitem fontes oficiais/secundárias e exigem data editorial.
- `servidor/catalogo.py` -- `modelos_visiveis` usa o extrato RAB vigente e `modelo_tecnicamente_completo`; preservar o filtro normal.
- `servidor/planos.py` -- `_aeronave_selecionada` valida elegibilidade antes de `montar`; manter a validação no servidor.
- `servidor/semente.py` -- semente normal contém dados históricos e aeródromos locais; não inserir perfis DEMO nela.
- `templates/plano_novo.html`, `templates/plano.html` e `servidor/pdf_plano.py` -- exibição atual de estimativas secundárias; reaproveitar os rótulos e preservar o aviso.
- `tests/conftest.py`, `tests/conftest_rota.py`, `tests/test_catalogo_aeronaves.py` e `tests/test_rota_pdf.py` -- fixtures, regras de elegibilidade, cálculos e apresentação existentes.
- `alembic/versions/` -- local das migrações; qualquer alteração de esquema precisa ser compatível com dados atuais.

## Tasks & Acceptance

**Execution:**
- [x] `app.py`, `servidor/modelos.py` -- adicionar configuração DEMO explícita e bloqueios de produção/armazenamento compartilhado, sem alterar o caminho normal.
- [x] `servidor/proveniencia.py`, `servidor/catalogo.py`, `servidor/planos.py`, `servidor/modelos.py`, `alembic/versions/` -- representar e aceitar fonte sintética somente no modo DEMO; manter fontes sintéticas inelegíveis no modo normal.
- [x] `servidor/semente_demo.py` -- carregar vinte perfis genéricos com unidades e dados completos de forma repetível, sem tocar na semente normal.
- [x] `app.py`, `templates/plano_novo.html`, `templates/plano.html`, `servidor/pdf_plano.py` -- identificar dados sintéticos e aviso não operacional em todas as superfícies relevantes.
- [x] `tests/` -- provar bloqueio de produção, isolamento, idempotência, exatamente vinte perfis, recusa no modo normal e rótulos em HTML/PDF.
- [x] `documentacao/operacao.md`, `documentacao/piloto.md` -- documentar preparação e uso restrito do ambiente DEMO, sem expor segredos.

**Acceptance Criteria:**
- Given modo DEMO em ambiente de desenvolvimento e armazenamento isolado, when a carga é executada duas vezes, then há exatamente vinte perfis identificados como sintéticos e nenhum dado fora desse armazenamento é alterado.
- Given o modo normal, when registros sintéticos existem no armazenamento, then a seleção e os cálculos os recusam.
- Given produção, armazenamento ausente ou compartilhado, when o modo DEMO é solicitado, then a inicialização falha explicitamente antes de qualquer escrita.
- Given um perfil sintético é mostrado em tela, resultado ou PDF, when seus valores são apresentados, then o rótulo sintético e o aviso não operacional permanecem visíveis.

## Implementation Notes

## Design Notes

A procedência atual exige data de publicação para fontes oficiais e secundárias. Dados gerados não têm data editorial; a implementação não deve preencher essa lacuna com a data de consulta nem simular uma publicação. A solução precisa manter a distinção de fonte sintética sem enfraquecer a validação das fontes rastreáveis.

## Verification

**Commands:**
- `uv run pytest tests/test_catalogo_aeronaves.py tests/test_tela_piloto.py tests/test_rota_pdf.py` -- expected: existing catalog, UI, calculation and PDF behavior remains valid.
- `uv run pytest` -- expected: full test suite passes, including DEMO isolation and production rejection.
