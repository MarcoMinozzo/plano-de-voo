---
title: 'Banco único e fim do modo DEMO'
type: 'feature'
created: '2026-11-25'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/specs/006-catalogo-demo-sintetico/'
  - '{project-root}/specs/007-proxies-aeronaves-demo/'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O produto mantém dois bancos de aplicação e depende de um modo DEMO para selecionar perfis sintéticos, embora o usuário esclareça que o sistema inteiro tem finalidade didática e não é usado para planejar voos reais.

**Approach:** Usar `DATABASE_URL` como única base de produto, remover o modo DEMO e manter nela os vinte perfis proxy sintéticos já existentes, sem pesquisa ou validação aeronáutica adicional. A interface e os documentos continuarão identificando esses valores como sintéticos, não validados e inadequados para uso real; a base de testes permanece isolada.

**Boundaries & Constraints**

**Always:** `DATABASE_URL` será a única configuração de banco do produto; `DATABASE_URL_TESTE` continuará isolada para testes; credenciais ficarão fora do repositório; o ROTAER e o RAB existentes na base `DATABASE_URL` serão preservados; um comando único de migração usará `DATABASE_URL_DEMO_ORIGEM` somente como fonte de leitura; importar exatamente os vinte perfis proxy sintéticos e seus valores, sem validação aeronáutica; mantê-los selecionáveis em categoria didática distinta dos modelos factuais; identificá-los visivelmente como sintéticos, não validados e sem correspondência comprovada com o modelo-alvo; preservar avisos de finalidade didática e de não autorização de voo; não importar pilotos nem planos; não alterar nem apagar a base antiga.

**Never:** remover o banco de testes isolado; manter os vinte perfis genéricos “Aeronave DEMO 01–20”; pesquisar ou validar os valores dos proxies como requisito da migração; alterar os valores técnicos existentes; apresentá-los como fatos, estimativas validadas ou dados operacionais do modelo-alvo; migrar pilotos ou planos da antiga base DEMO; apagar ou sobrescrever dados existentes em qualquer banco.

**Decisões do usuário:** Manter os vinte proxies existentes mesmo sem validação técnica; não gastar mais tempo pesquisando ou validando dados de aeronaves. Remover os vinte perfis genéricos. Usar a base atual `DATABASE_URL` como canônica, preservando seu ROTAER e RAB; importar da antiga base DEMO somente os vinte proxies sintéticos, sem pilotos nem planos. Preservar a antiga base DEMO intacta e manter a base de testes separada.

## I/O & Edge-Case Matrix

| Cenário | Entrada / Estado | Comportamento esperado | Tratamento |
|---|---|---|---|
| Inicialização | `DATABASE_URL` configurada; antigas variáveis DEMO ausentes ou presentes | App e Alembic usam a única URL de produto e ignoram/removem configuração DEMO conforme transição documentada | Sem fallback a outra base |
| Ambiente inválido | `DATABASE_URL` ausente ou inválida | Inicialização falha explicitamente antes de abrir sessão | Mensagem sem segredo |
| Perfis proxy | Os vinte proxies existentes têm valores sintéticos sem validação por modelo | Os vinte ficam selecionáveis em categoria didática separada, com valores preservados; tela, resultado e PDF identificam claramente que não são validados | Não bloquear por ausência de referência aplicável |
| Perfis genéricos | A base DEMO contém “Aeronave DEMO 01–20” | Esses vinte perfis não são importados nem oferecidos | Nenhum |
| Migração | Base `DATABASE_URL` contém ROTAER/RAB; base DEMO contém proxies e pode conter outros dados | Importar somente os vinte proxies; manter catálogos atuais da base canônica, não migrar pilotos/planos e não alterar a origem | Transação aborta sem sobrescrever dados canônicos em caso de conflito |
| Reexecução | Os vinte perfis e fontes já existem no destino com os mesmos valores | Não duplica nem altera os registros | Colisão com dados divergentes aborta |
| Origem incompleta | A base antiga não contém exatamente os vinte proxies esperados | Migração informa os perfis ausentes e não altera o destino | Abortar antes do commit |

</frozen-after-approval>

## Code Map

- `servidor/ambiente.py`, `app.py` e `alembic/env.py` selecionam a base e condicionam sintéticos ao DEMO; `tests/conftest.py` já isola `DATABASE_URL_TESTE`.
- `servidor/semente_demo.py` cria 20 genéricos e 20 proxies; `servidor/perfis_demo.py` define os proxies. `servidor/modelos.py` permite `Aeronave.extrato_id` nulo e relaciona fontes técnicas por aeronave.
- `servidor/importar_rotaer_demo.py` usa duas sessões e transação, mas copia ROTAER do banco canônico para o DEMO; criar importação específica, sem copiar ROTAER nem o `ExtratoRab` DEMO.
- `servidor/catalogo.py`, `servidor/proveniencia.py` e `servidor/planos.py` filtram completude e elegibilidade; separar proxies do limite de 30 modelos factuais e permitir cálculo didático sem validação de fonte.
- `servidor/pdf_plano.py`, templates, documentação e testes cobrem rótulos e modo; reutilizar avisos atuais de não uso real. As specs 006/007 devem ser marcadas como substituídas.

## Tasks & Acceptance

**Execution:**
- [ ] Simplificar `servidor/ambiente.py`, `app.py` e `alembic/env.py` para usar somente `DATABASE_URL`; manter `tests/conftest.py` isolado em `DATABASE_URL_TESTE`.
- [ ] Alterar `servidor/semente_demo.py`, `servidor/perfis_demo.py` e `servidor/catalogo.py` para manter selecionáveis os vinte proxies atuais e não criar nem oferecer os vinte perfis genéricos.
- [ ] Atualizar `servidor/proveniencia.py`, `servidor/planos.py`, `servidor/pdf_plano.py`, `templates/plano_novo.html` e `templates/plano.html` para aceitar proxies sem validação de fonte e identificá-los como sintéticos não validados, sem rótulo DEMO.
- [ ] Criar comando idempotente com `DATABASE_URL_DEMO_ORIGEM` para copiar somente as vinte aeronaves proxy e seus seis registros de fonte, gerar IDs de destino, não copiar o extrato DEMO nem os vinte genéricos, e abortar em conflito ou origem incompleta sem alterar origem ou destino.
- [ ] Atualizar documentação, marcar `specs/006-catalogo-demo-sintetico/` e `specs/007-proxies-aeronaves-demo/` como substituídas e ajustar testes de ambiente, seleção, importação, cálculo e PDF.

**Acceptance Criteria:**
- Dada qualquer configuração antiga de DEMO, quando app e Alembic iniciam, então usam somente `DATABASE_URL`; testes continuam em `DATABASE_URL_TESTE`.
- Dada a base canônica com ROTAER/RAB e a antiga base com os proxies, quando a importação roda, então acrescenta exatamente os vinte proxies e suas fontes, sem duplicar catálogos nem alterar a origem.
- Dado que os perfis já foram importados, quando a importação é repetida com os mesmos dados, então termina sem duplicar nem alterar registros; conflito divergente ou origem incompleta aborta sem alteração e informa a causa.
- Dado um proxy não validado, quando é selecionado e calculado, então permanece disponível e tela/PDF identificam os valores como sintéticos e não representativos do modelo-alvo; perfis genéricos não aparecem.
- Dado um plano com proxy, quando exibido ou impresso, então preserva o aviso didático de não uso real; a suíte permanece isolada do banco do produto.

## Implementation Notes

- A implementação atual gera os seis campos dos proxies por interpolação determinística em duas faixas genéricas. Por decisão expressa do usuário, os vinte perfis e seus valores atuais serão preservados para uso didático sem validação adicional. Não apresentar as faixas/referências genéricas como prova de compatibilidade com o modelo-alvo.

## Design Notes

A base atual em `DATABASE_URL` permanece canônica. A migração acrescenta os proxies sem substituir seu ROTAER/RAB pelo extrato sintético DEMO; a base antiga permanece intacta como recuperação.

## Verification

**Commands:**
- `pytest tests/test_ambiente_demo.py tests/test_semente_demo.py tests/test_proveniencia.py tests/test_rota_pdf.py` -- esperado: seleção normal dos vinte proxies, isolamento de testes e avisos sintéticos corretos.
- Testes direcionados da importação em bancos isolados -- esperado: cópia idempotente de vinte proxies, sem perda, colisão silenciosa ou mutação da origem.
- `git diff --check` -- esperado: sucesso.
