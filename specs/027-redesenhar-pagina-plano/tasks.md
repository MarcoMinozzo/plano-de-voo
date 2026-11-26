---
description: "Tarefas para redesenhar a página do plano"
---

# Tasks: Redesenho da página do plano

**Input**: Design documents from `specs/027-redesenhar-pagina-plano/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Regressões focadas cobrem renderização, contatos oficiais, estados das camadas e legibilidade do mapa.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode ser executada em paralelo, sem conflito de arquivos ou dependências pendentes.
- **[Story]**: história relacionada (`US1`, `US2`).
- Cada tarefa indica o caminho exato dos arquivos afetados.

## Path Conventions

- Aplicação Flask/Jinja em `app.py`, `servidor/`, `templates/`, `static/`, `tests/` e `documentacao/`.

## Phase 1: Setup

**Purpose**: A pilha existente e os scripts de teste/build já atendem à feature.

Nenhuma tarefa de setup.

## Phase 2: Foundational

**Purpose**: Não há infraestrutura bloqueadora compartilhada.

Nenhuma tarefa fundacional.

## Phase 3: User Story 1 - Entender a rota e os dados do plano (Priority: P1) 🎯 MVP

**Goal**: Exibir rota completa, dados oficiais dos aeródromos e alertas de forma clara e sem alterar os cálculos ou o PDF.

**Independent Test**: Renderizar plano de teste com escalas, alertas, contatos publicados e ausentes; conferir nomes, dados oficiais e aviso explícito de ausência.

### Tests for User Story 1

- [X] T001 [P] [US1] Adicionar regressões em `tests/test_tela_piloto.py` para sequência completa, nomes por trecho, dados de origem/destino, alerta textual em vermelho, orientação removida e impressão mantida no topo.
- [X] T002 [P] [US1] Adicionar casos em `tests/test_catalogo_aerodromos.py` para contatos oficiais publicados, ausentes e removidos quando a emenda vigente deixa de publicá-los.

### Implementation for User Story 1

- [X] T003 [US1] Adicionar telefone, e-mail e marcador `contatos_rotaer_verificados` em `servidor/modelos.py` e criar migração aditiva em `alembic/versions/a7c9e2f4b6d1_adicionar_contatos_aerodromo.py`; seguir `data-model.md`: AISWEB/ROTAER somente, campo ausente fica nulo e registros antigos permanecem válidos.
- [X] T004 [US1] Interpretar telefone/e-mail somente quando publicados em `servidor/rotaer_parse.py` e sincronizar valores da emenda vigente em `servidor/catalogo.py`, limpando contato obsoleto quando ausente na fonte atual.
- [X] T005 [US1] Passar ao template os aeródromos já resolvidos em `app.py:ver_plano`, sem adicionar chamadas externas ao abrir o plano.
- [X] T006 [US1] Reorganizar `templates/plano.html` em card principal responsivo de aproximadamente 80% da viewport larga; exibir rota completa, nomes, dados oficiais, alertas vermelhos e aviso didático; remover “Como ler este plano” e o link PDF do rodapé, mantendo impressão no topo.

**Checkpoint**: A rota e os dados oficiais são legíveis, contatos ausentes não são inventados, alertas são claros e o PDF permanece inalterado.

## Phase 4: User Story 2 - Consultar o mapa sem perder a rota (Priority: P1)

**Goal**: Oferecer controles compactos dentro do mapa e manter ruas e rota legíveis com as camadas meteorológicas disponíveis.

**Independent Test**: Com cada radar ativado isoladamente, verificar a base, a rota, a independência das fontes e os estados disponíveis/indisponíveis.

### Tests for User Story 2

- [X] T007 [US2] Adicionar regressões de controles em `tests/test_tela_piloto.py` para ruas ativas, Google desativado sem chave, WAC indisponível compacta, OpenAIP não configurado ausente, radares desligados sem mensagem redundante e atribuição RainViewer quando ativo.

### Implementation for User Story 2

- [X] T008 [US2] Atualizar os controles e camadas em `templates/plano.html`: botões liga/desliga no topo interno do mapa, Google desativado sem chave, REDEMET e RainViewer independentes, WAC indisponível concisa, sem aviso OpenAIP não configurado e sem máscara de cobertura RainViewer desenhada sobre a base; preservar validação geográfica, rota e tratamento de falha.

**Checkpoint**: Cada fonte mantém sua identidade, a rota continua visível e a máscara não obscurece o mapa de ruas.

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Atualizar estilos compilados, documentação e validar a integração completa.

- [X] T009 Executar `npm run css:build` para gerar `static/css/tailwind.css` com as classes novas do layout e dos controles.
- [X] T010 Atualizar `documentacao/piloto.md` com os controles, fontes e avisos compactos do mapa.
- [X] T011 Executar `uv run pytest --no-cov tests/test_tela_piloto.py tests/test_tempo.py tests/test_catalogo_aerodromos.py`, validar a migração de contatos no ambiente de teste e executar `git diff --check`.
- [X] T012 Seguir `specs/027-redesenhar-pagina-plano/quickstart.md` no navegador a 390 px e 1440 px, testando teclado/toque, contatos publicados/ausentes e cada radar separadamente.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: já atendido; nenhuma dependência nova.
- **Foundational (Phase 2)**: já atendido; nenhuma tarefa bloqueadora.
- **US1 (Phase 3)**: independente; testes T001/T002 precedem a implementação.
- **US2 (Phase 4)**: executada após US1 para evitar conflito nas alterações de `templates/plano.html` e `tests/test_tela_piloto.py`.
- **Polish (Phase 5)**: depende da conclusão das duas histórias.

### User Story Dependencies

- **US1 (P1)**: pode iniciar sem outra história.
- **US2 (P1)**: comportamento do mapa é independente dos contatos, mas deve ser integrado após US1 porque as duas histórias alteram o mesmo template e arquivo de teste.

### Within Each User Story

- Testes falham antes de implementar o comportamento.
- T003 precede T004; T004 e T005 antecedem a apresentação dos contatos em T006.
- T006 precede T007/T008 por compartilharem o template.
- T009/T010 podem ser preparados em arquivos distintos depois que os textos e classes finais estiverem definidos; T011 e T012 validam o resultado integrado.

### Parallel Opportunities

- T001 e T002 podem ser executadas em paralelo: atuam em arquivos de teste diferentes.
- T010 pode ser preparado em paralelo às mudanças de template após a definição dos textos finais.
- Não paralelizar tarefas que alteram `templates/plano.html` ou `tests/test_tela_piloto.py`.

## Implementation Strategy

1. Implementar US1 primeiro como MVP: testes, contatos oficiais opcionais, dados da rota, alertas e composição principal.
2. Executar os testes de US1 antes de iniciar os controles do mapa.
3. Implementar US2 preservando a independência REDEMET/RainViewer e verificar visualmente o overlay.
4. Compilar Tailwind, atualizar a documentação e executar os testes e cenários do quickstart.

## Notes

- [P] indica arquivos sem conflito e sem dependência pendente.
- Não alterar cálculos, dados de rota, autorização por piloto ou PDF.
- A camada Google continua desativada neste escopo; não adicionar chave ao repositório nem integrar tiles Google sem configuração e revisão próprias.
