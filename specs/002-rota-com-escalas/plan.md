# Implementation Plan: Rota com escalas

**Branch**: `002-rota-com-escalas` | **Date**: 2026-11-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-rota-com-escalas/spec.md`

## Summary

O piloto continua informando origem, destino e hora. O servidor escolhe a rota e as escalas usando os aeródromos da emenda vigente do ROTAER e os modelos do Registro Aeronáutico Brasileiro. A seleção é formada depois de filtrar modelos completos e ordenar por frota; no máximo os 30 primeiros podem ser oferecidos. Os mesmos critérios se aplicam a todos os modelos, sem exceção por nome. Modelos incompletos e os completos além do limite ficam em espera, ocultos e recusados também em `POST` e `PUT`. Valores podem vir de fonte oficial ou secundária rastreável, sempre com procedência por campo; conflitos entre fontes aplicáveis priorizam a publicação mais recente e mantêm a divergência registrada. Dados secundários são estimativas didáticas identificadas na seleção, resultado e PDF. Sem extrato RAB vigente, a lista fica indisponível e vazia. A conta permanece no servidor e não ganha dependências.

Se o AISWEB não fornecer uma emenda vigente, a lista local pode ser consultada e selecionada na tela, mas não valida um plano e não pode alimentar o cálculo.

A abordagem está em [research.md](./research.md). Não há biblioteca nova.

## Technical Context

**Language/Version**: Python 3.10 ou mais novo

**Primary Dependencies**: As já nomeadas na constituição 4.0.0: Flask 3.0.0, SQLAlchemy 2, psycopg 3, Alembic, requests 2.31.0, reportlab 4.0.7, Leaflet 1.9 pelo CDN. Nenhuma dependência nova.

**Storage**: PostgreSQL 16. Reutiliza os campos técnicos existentes em `Aeronave` e acrescenta procedência estruturada por campo, incluindo publicador, referência, data verificável, modelo/variante e perfil quando aplicável. `manual_estado="gravado"` indica dados completos conferidos, oficiais ou secundários; não certifica validade operacional. O extrato importado por `RAB_EXTRATO` fornece a frota e a ordem. A rota do plano é uma lista ordenada de trechos. Não há dados verificáveis dos 30 modelos no repositório, portanto nenhum conjunto de 30 é presumido ou inventado.

**Testing**: pytest, com RAB, fontes e valores fictícios apenas nos testes. Validar completude antes do corte, ordem decrescente de frota, desempate estável por nome, teto de 30, ausência de modelos sem RAB vigente, procedência por campo, escolha da fonte aplicável mais recente, registro de conflitos, rótulo didático em todos os canais e recusa em `POST` e `PUT` de identificadores incompletos ou fora dos 30. Validar que todo registro legado sem procedência verificável fica inelegível, sem regra específica por modelo. Não copiar valores técnicos reais para os testes.

Sem ROTAER vigente, verificar que a lista local é identificada para consulta e que `POST` e `PUT` não criam nem calculam planos.

**Target Platform**: O mesmo processo Flask local do plano direto.

**Project Type**: Aplicação web de um processo, páginas servidas pelo servidor.

**Performance Goals**: Montar a rota de um par de aeródromos brasileiros em tempo de uma interação de formulário, sem varrer trechos mais longos do que o alcance de planejamento dos dados técnicos selecionados.

**Constraints**: Somente voo visual diurno. Sem dado técnico inventado, transferido ou interpolado. Valores podem vir de POH/AFM ou fonte técnica secundária rastreável e aplicável; registrar unidade, publicador, referência, data e modelo/variante por campo, além de edição/revisão e página/tabela quando houver manual. Entre fontes aplicáveis conflitantes, priorizar a mais recente mesmo se menos específica, registrar divergência e incerteza e não fazer média; sem data ou aplicabilidade verificável, deixar o campo indisponível. Combustível utilizável exclui combustível inutilizável. Velocidade e consumo vêm do mesmo perfil nominal de cruzeiro. A completude só é declarada após conferência humana da fonte e de todos os campos obrigatórios. Valores secundários são exibidos como estimativas didáticas, sem aptidão operacional. Sem RAB vigente, não há seleção nem plano novo com aeronave. Sem coordenada inventada, vento de cauda sem cobertura oficial ou fórmula no JavaScript. Chaves e extrato bruto fora do repositório. Texto em português. O resultado não autoriza o voo.

**Scale/Scope**: A emenda vigente do ROTAER para aeródromos de avião e os modelos de avião pequeno do extrato público vigente do RAB. A caixa de seleção oferece até 30 modelos completos em ordem de frota. Um plano continua de um piloto.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição 4.0.0. O nome do projeto é Plano de voo.
O limite do MVP segue a seção “Catálogo nacional e rota”: somente modelos
completos com fonte técnica rastreável podem ser ordenados por frota e
limitados a 30; valores secundários são didáticos e não operacionais; sem
extrato vigente, a seleção fica indisponível e vazia.

| Portão | Antes da pesquisa | Depois do desenho |
| --- | --- | --- |
| Spec antes do código | Passa. Este plano não altera o servidor. | Passa. Artefatos em `specs/002-rota-com-escalas/`. |
| Cálculo no servidor | Passa. A rota e as escalas ficam no servidor. | Passa. O mapa só desenha trechos já calculados. |
| Unidade, fonte e falha visível | Passa. | Passa. Emenda, manual, vento e pôr do sol têm estado indisponível. |
| Catálogo só da emenda vigente | Passa. | Passa. Sem chave ou sem emenda, a lista local é apenas para consulta; o servidor recusa planos sem ROTAER vigente. |
| Fonte, unidade e variante por valor | Passa. Não se transfere dado entre modelos; dados secundários podem ser usados só para fins didáticos. | Passa. Cada valor tem procedência verificável; conflitos e estimativas são explícitos. |
| Plano só do piloto da sessão | Passa. Reusa a sessão do plano direto. | Passa. |
| Nenhuma dependência nova | Passa. `requests` já busca o AISWEB. | Passa. |

## Project Structure

### Documentation (this feature)

```text
specs/002-rota-com-escalas/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/api-rota.md
└── tasks.md
```

### Source Code (repository root)

```text
servidor/
├── catalogo.py             # ROTAER, RAB vigente e elegibilidade dos 30 modelos
├── rota.py                 # escolha da rota e das escalas
├── calculo.py              # trecho, já existente, passa a ser chamado por perna
├── planos.py               # grava a rota no plano
├── semente.py              # dados e procedência por campo, conferidos segundo regra uniforme
└── pdf_plano.py            # imprime os trechos

app.py                       # propaga o estado do catálogo de aeronaves à tela
templates/plano.html        # lista os trechos e desenha a linha já calculada
templates/plano_novo.html   # origem e destino no catálogo; não pede a escala
documentacao/piloto.md      # o que é escala, catálogo indisponível e estimativas didáticas
documentacao/operacao.md    # preparação de RAB_EXTRATO fora do repositório
alembic/versions/            # migração da procedência técnica por campo e estado legado
tests/test_catalogo_aeronaves.py  # completude, exatidão, ordenação, limite e indisponibilidade
tests/test_rota.py                 # recusa de aeronave fora da seleção em POST e PUT
tests/test_tela_piloto.py          # estado indisponível e lista vazia na tela
```

**Structure Decision**: Continua o processo Flask e acrescenta uma tabela relacional `FonteTecnicaAeronave`, com uma linha por campo e fonte, mantendo os valores selecionados nos campos escalares atuais de `Aeronave`. `modelos_visiveis` deve aplicar a todos os modelos a mesma verificação de completude, ordenar por frota decrescente e nome crescente em empate, e então limitar a 30. `montar` deve verificar que o modelo pertence à mesma seleção vigente, não apenas que `manual_estado` está gravado. A seleção de fonte escolhe a mais recente entre as que declaram aplicabilidade ao modelo, conserva referências conflitantes e não combina valores. `carregar_rab` só pode atualizar a frota por correspondência canônica validada; fabricante, PMD, substring ou candidato único não provam aplicabilidade técnica. `manual_estado="gravado"` indica completude conferida, não certificação operacional. A carga RAB indisponível não pode usar modelos locais como fallback. Registros antigos sem procedência verificável permanecem inelegíveis, com valores numéricos preservados e sem condição por nome. O navegador não ganha framework nem fórmula.

## Complexity Tracking

Nenhuma violação da constituição. A carga do ROTAER e do RAB usa o `requests` já justificado. Não entra biblioteca de grafo.
