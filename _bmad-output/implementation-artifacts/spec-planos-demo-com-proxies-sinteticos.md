---
title: 'Planos DEMO com proxies sintéticos de aeronaves'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47f3a6317435dd6f2ba6b56e43b3e85163d66f8a'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/006-catalogo-demo-sintetico/spec.md'
  - '{project-root}/specs/002-rota-com-escalas/spec.md'
  - '{project-root}/_bmad-output/specs/spec-fontes-secundarias-aeronaves/secondary-sources.md'
  - '{project-root}/_bmad-output/planning-artifacts/research/domain-dados-oficiais-de-aeronaves-do-mvp-2026-11-24/digests/candidates-r1-3.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A base DEMO tem perfis genéricos, mas é preciso testar planos usando proxies sintéticos associados a modelos-alvo, junto aos dados de aeródromo e meteorologia da aplicação.

**Approach:** Disponibilizar proxies DEMO com valores dentro de faixas justificadas por referências rastreáveis e usá-los no fluxo de planos existente. Aeródromos e condições de voo continuam exclusivamente provenientes das fontes oficiais; o resultado permanece não operacional.

## Decisões do usuário

- Usar o ranking preliminar do RAB e continuar a triagem até 20 modelos elegíveis; substituir candidatos que excedam o limite ou não tenham evidência suficiente.
- Manter os 20 perfis genéricos e os proxies selecionáveis no DEMO. O catálogo DEMO deve comportar até 40 perfis para não ocultar proxies; o limite do catálogo normal permanece 30.

## Boundaries & Constraints

**Always:** Restringir proxies a `development` e PostgreSQL DEMO dedicado; registrar por campo unidade, faixa de teste, evidências, aplicabilidade, método, versão/seed e incerteza; justificar faixas por fonte aplicável ao modelo ou por duas fontes de modelos comparáveis; continuar a triagem até 20 elegíveis, sem ativar campos sem evidência; exibir proxies e perfis genéricos no catálogo DEMO e preservar planos existentes; rotular seleção, resultado e PDF; exigir ROTAER vigente; usar AWC, REDEMET e AISWEB pelos fluxos existentes; mostrar indisponibilidade; manter o catálogo normal inalterado; fazer migrações aditivas.

**Never:** Apresentar proxies como valores reais, certificados ou limites operacionais; sintetizar aeródromos, coordenadas, METAR/TAF, vento, cartas, radar ou pôr do sol; ativar campo sem evidência suficiente; usar proxies fora do DEMO ou para voo real; fazer chamadas externas nos testes.

## I/O & Edge-Case Matrix

| Cenário | Entrada/Estado | Comportamento esperado | Erro/indisponibilidade |
|----------|----------------|------------------------|------------------------|
| Plano DEMO válido | Proxy completo e ROTAER vigente | Cria plano com aeródromos da emenda e rótulo proxy | Nenhum campo sintético é tratado como factual |
| Catálogo DEMO completo | 20 perfis genéricos e até 20 proxies elegíveis | Ambos os grupos podem ser selecionados; o limite DEMO não oculta proxies | O catálogo normal continua limitado a 30 |
| ROTAER ausente | DEMO sem emenda vigente | Não cria rota | Informa indisponibilidade do ROTAER |
| Fonte oficial ausente | AWC/REDEMET/AISWEB sem resposta ou cobertura | Mostra indisponibilidade; só vento oficial que cobre o trecho é aplicado | Não presume condição favorável |
| Proxy inválido ou modo normal | Campo incompleto/fora da faixa, ou tentativa fora do DEMO | Oculta ou recusa o perfil | Erro explícito; sem fallback |

</frozen-after-approval>

## Code Map

- `servidor/modelos.py:130`, `servidor/proveniencia.py:24,116,176` -- `FonteTecnicaAeronave` já guarda valor e procedência, mas não faixa, método, seed/versão ou incerteza; validação seleciona fonte e exige campos técnicos completos.
- `servidor/semente_demo.py:14,40`, `servidor/catalogo.py:91` -- a semente é idempotente e cria 20 perfis genéricos; `modelos_visiveis` filtra completude e limita a 30. Em DEMO, comportar até 40 registros para expor todos os genéricos e proxies; manter o limite normal.
- `servidor/planos.py:162,183,199` -- `montar` aceita sintéticos apenas quando habilitado, exige ROTAER no DEMO e persiste procedência e dados retornados por `tempo_mod.buscar`.
- `servidor/tempo.py:302`, `templates/plano_novo.html:25,31`, `templates/plano.html:21,71`, `servidor/pdf_plano.py:36` -- manter fontes oficiais e estados indisponíveis; estender a exibição existente de procedência nas três superfícies.
- `app.py:385`, `alembic/versions/` -- a rota de catálogo já inclui procedência; acrescentar campos via migração aditiva, sem alteração no banco normal.
- `_bmad-output/planning-artifacts/research/domain-dados-oficiais-de-aeronaves-do-mvp-2026-11-24/digests/candidates-r1-3.md` -- ranking RAB preliminar; não é certificação de classe, PMD ou completude técnica.
- `tests/test_catalogo_aeronaves.py`, `tests/test_semente_demo.py`, `tests/test_rota.py`, `tests/test_tempo.py`, `tests/test_tela_piloto.py`, `tests/test_rota_pdf.py` -- reutilizar testes de seleção, idempotência, ROTAER obrigatório, indisponibilidade e apresentação; completar o percurso DEMO com fontes simuladas.

## Tasks & Acceptance

**Execution:**
- [x] `servidor/modelos.py`, `alembic/versions/` -- criar migração aditiva e persistir limites, evidências, aplicabilidade, método, versão/seed e incerteza por campo, preservando registros existentes.
- [ ] `servidor/proveniencia.py`, `servidor/catalogo.py`, `servidor/semente_demo.py` -- carregar até 20 proxies elegíveis com valores/faixas/evidências, validar relações físicas, manter carga idempotente e permitir até 40 perfis selecionáveis somente no DEMO. **Pendente:** comprovar individualmente a elegibilidade RAB/PMD e comparabilidade de todos os 20 alvos; a lista atual ainda não satisfaz essa verificação.
- [x] `servidor/planos.py`, `app.py` -- manter o fluxo DEMO, guardar procedência do proxy e exigir ROTAER vigente.
- [x] `templates/plano_novo.html`, `templates/plano.html`, `servidor/pdf_plano.py` -- exibir faixa, evidências, método, incerteza e aviso não operacional.
- [x] `tests/test_catalogo_aeronaves.py`, `tests/test_migracao_aeronaves.py`, `tests/test_semente_demo.py`, `tests/test_rota.py`, `tests/test_tempo.py`, `tests/test_tela_piloto.py`, `tests/test_rota_pdf.py`, `tests/test_proveniencia.py`, `tests/test_rotaer_demo.py` -- testar elegibilidade, migração, repetição, fontes simuladas/indisponíveis e bloqueio normal.
- [x] `documentacao/operacao.md`, `documentacao/piloto.md` -- documentar configuração oficial e limites DEMO.

**Acceptance Criteria:**
- Given qualquer campo sintético carregado, when a procedência é consultada, then valor, unidade, faixa, evidências, método, versão/seed e incerteza são retornados juntos.
- Given um proxy apresentado ao piloto, when ele aparece na seleção, resultado ou PDF, then cada superfície o identifica como “DEMO — proxy sintético” e informa que não corresponde a dado factual nem autoriza voo.
- Given 20 perfis genéricos e até 20 proxies elegíveis, when o catálogo é consultado, then ambos os grupos são selecionáveis em DEMO e o catálogo normal continua limitado a 30.
- Given perfis genéricos e planos históricos, when a nova carga DEMO é repetida, then esses registros permanecem preservados e nenhum dado é alterado no banco normal.

## Implementation Notes

- Migração aditiva, validação por faixa/evidência, catálogo DEMO de até 40 opções, cópia isolada do ROTAER e exposição do snapshot do proxy implementados.
- A cópia da emenda vigente foi testada em SQLite com repetição e preservação de aeronaves, pilotos e planos da base DEMO; a ordem de ativação evita violar o índice de emenda vigente.
- Verificação: `uv run pytest -k 'not test_mutation_score'` — 82 testes passaram. `uv run pytest` também executou o teste mutacional, que falhou com 52,5% abaixo do mínimo configurado de 56%; a falha está no alvo `servidor/calculo.py`, fora desta implementação.
- Provisionamento no PostgreSQL não executado: `DATABASE_URL_DEMO` não está configurada neste ambiente. O fluxo recusou conectar, sem fallback para a base normal.
- A base local de pesquisa confirma elegibilidade de somente uma parte dos alvos. Não considerar os 20 proxies atuais como aprovados até concluir a verificação individual indicada acima.

## Spec Change Log

## Review Triage Log

## Design Notes

A faixa limita somente a geração de valores de teste. A associação aos modelos é um alvo didático, não valida uma aeronave real. Os 20 perfis genéricos continuam disponíveis em DEMO, junto aos proxies; perfis e planos antigos são preservados. Proxies sem evidência suficiente não ficam elegíveis.

## Verification

**Commands:**
- `uv run pytest tests/test_catalogo_aeronaves.py tests/test_migracao_aeronaves.py tests/test_semente_demo.py tests/test_rota.py tests/test_tempo.py tests/test_tela_piloto.py tests/test_rota_pdf.py` -- expected: DEMO seleciona genéricos e proxies, o normal mantém o limite de 30, e rotas com fontes simuladas passam.

**Manual checks:**
- A base normal contém a emenda oficial ROTAER AMDT 47/26 e 4.519 aeródromos; a base DEMO ainda não tem esses registros. Copiar apenas as tabelas oficiais de emenda/aeródromo para o banco DEMO, sem dependência da API AISWEB no carregamento. Credenciais REDEMET/AISWEB ausentes afetam somente vento, carta e pôr do sol; testes usam fixtures e respostas simuladas.
