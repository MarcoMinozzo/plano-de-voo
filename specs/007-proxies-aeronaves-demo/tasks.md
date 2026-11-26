# Tasks: Proxies de aeronaves em DEMO

**Input**: Documentos de design em `specs/007-proxies-aeronaves-demo/`

**Pré-requisitos**: `plan.md`, `spec.md`, `research.md`, `data-model.md` e `contracts/catalogo-demo.md`

**Testes**: Incluir testes focados para intervalos, elegibilidade, isolamento, repetição da carga e percurso DEMO; usar fixtures para fontes externas.

## Formato

- `[ID] [P?] [USx] Descrição` — `[P]` indica trabalho independente em arquivo distinto.
- `US1`: planejar usando proxy; `US2`: conferir origem e limites; `US3`: isolar DEMO e repetir a carga.

## Fase 1: Fundação

**Objetivo**: Persistir metadados novos sem invalidar fontes oficiais ou planos existentes.

- [x] T001 [P] Escrever teste de migração aditiva para os metadados de faixa e geração em `tests/test_migracao_aeronaves.py`.
- [x] T002 Criar migração Alembic para os campos opcionais descritos em `specs/007-proxies-aeronaves-demo/data-model.md`, preservando registros existentes em `alembic/versions/`.

## Fase 2: User Story 2 — Conferir a origem e os limites (P1)

**Objetivo**: Garantir que cada campo sintético selecionável tenha intervalo, evidência aplicável e geração reproduzível.

**Teste independente**: Validar os 20 genéricos e os proxies ativos; confirmar que valores fora da faixa ou sem evidência não são elegíveis.

- [x] T003 [P] Escrever testes de faixa, metadados ausentes, referências comparáveis, relações físicas e perfil comum de velocidade/consumo em `tests/test_proveniencia.py`.
- [X] T004 **Supersedido por 015**: a política atual mantém os perfis sintéticos sem validar aplicabilidade ao modelo associado; não foi feita pesquisa de fontes nem declarada comprovação factual.
- [x] T005 Implementar validação dos metadados sintéticos e dos limites em `servidor/proveniencia.py`; manter fontes não sintéticas compatíveis.
- [x] T006 Atualizar a apresentação de procedência, incluindo a faixa, as referências, o método, a versão/semente, a incerteza e “data editorial não se aplica”, em `servidor/proveniencia.py`.

## Fase 3: User Story 3 — Manter o isolamento DEMO e repetir a carga (P1)

**Objetivo**: Provisionar dados oficiais restritos ao DEMO e manter a carga idempotente, sem afetar o catálogo normal nem o histórico.

**Teste independente**: Repetir a carga em banco isolado, conferir perfis/planos existentes e validar que nenhum proxy é exposto no modo normal.

- [x] T007 [P] Escrever testes do provisionamento ROTAER: URLs distintas, apenas emenda vigente e aeródromos copiados, repetição idempotente e nenhuma cópia de pilotos/planos em `tests/test_rotaer_demo.py`.
- [x] T008 Implementar o comando explícito de transferência somente do ROTAER oficial da base normal para a base DEMO em `servidor/importar_rotaer_demo.py`; o runtime da aplicação DEMO não pode conectar à base normal.
- [x] T009 Escrever testes de repetição da semente, preservação dos 20 genéricos e planos existentes em `tests/test_semente_demo.py` e `tests/test_rota_pdf.py`.
- [X] T010 **Supersedido por 015**: o runtime não semeia proxies validados em DEMO; a estratégia vigente importa os perfis didáticos existentes sem validar ou gerar seus valores.
- [x] T011 Escrever testes do limite DEMO 40, limite normal 30 e exclusão de fontes sintéticas no modo normal em `tests/test_catalogo_aeronaves.py` e `tests/test_tela_piloto.py`.
- [x] T012 Aplicar o limite condicional 40/30 e manter a filtragem de elegibilidade em `servidor/catalogo.py`.

## Fase 4: User Story 1 — Planejar usando proxy de modelo (P1)

**Objetivo**: Completar o percurso de seleção e criação de plano usando ROTAER e respostas meteorológicas oficiais simuladas.

**Teste independente**: Criar um plano de teste com proxy completo e ROTAER fixture vigente; confirmar snapshot de procedência e aviso DEMO.

- [x] T013 Escrever testes de criação do plano com proxy, ROTAER fixture e respostas oficiais simuladas, além de recusa sem ROTAER e indisponibilidade explícita quando uma fonte oficial falha, em `tests/test_rota.py`, `tests/test_tempo.py` e `tests/test_rota_pdf.py`.
- [x] T014 Preservar no snapshot do plano os valores e metadados usados no cálculo e manter recusas/indisponibilidades explícitas em `servidor/planos.py`.
- [x] T015 Escrever testes dos rótulos e campos de procedência na seleção, resultado e PDF em `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py`.
- [x] T016 Exibir “DEMO — proxy sintético”, a associação somente como alvo de teste, a faixa e o aviso não operacional em `app.py`, `templates/plano_novo.html`, `templates/plano.html` e `servidor/pdf_plano.py`.
- [x] T019 [US1] Remover os menus de fontes técnicas do formulário de novo plano e exibir somente o nome cadastrado em cada opção; preservar avisos DEMO fora da lista e procedência detalhada no resultado/PDF, com testes em `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py`.
- [x] T020 [US1] Ocultar perfis genéricos da seleção DEMO e exibir proxies somente pelo nome do modelo-alvo, sem “Proxy DEMO”; manter um aviso geral de dados sintéticos e validar o fluxo em `tests/test_tela_piloto.py` e `tests/test_rota_pdf.py`.

## Fase 5: Documentação e verificação

- [x] T017 Atualizar `documentacao/operacao.md` e `documentacao/piloto.md` para documentar a transferência ROTAER, as fontes oficiais e as restrições dos proxies DEMO.
- [X] T018 **Supersedido por 015**: a configuração e o quickstart de banco DEMO foram removidos; a suíte atual passou (136 testes). Nenhuma validação operacional em base DEMO foi executada.

## Dependências e ordem de execução

- T001 precede T002; T003 precede T005; T004 precede T010.
- T007 precede T008; T009 precede T010; T011 precede T012.
- T013 precede T014; T015 precede T016; T016 precede T019; T019 precede T020.
- T002, T005, T008, T010 e T012 precisam estar concluídas antes do percurso ponta a ponta T013.
- T017 e T018 dependem da conclusão das histórias.
- O teste de aceitação da matriz de I/O precisa cobrir: plano válido, catálogo completo, ROTAER ausente, falha de fonte oficial, proxy inválido e tentativa no modo normal.

## Estratégia de entrega

1. Concluir a migração e a validação de procedência.
2. Curar fontes/faixas e preparar os perfis antes de torná-los elegíveis.
3. Implementar a transferência oficial do ROTAER, a semente idempotente e o limite exclusivo DEMO.
4. Completar tela, resultado e PDF; validar o fluxo com fixtures.
5. Executar a suíte focada e depois a suíte completa.
