# Implementation Plan: Corrigir carga do ROTAER

**Branch**: `014-corrigir-carga-rotaer` | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/014-corrigir-carga-rotaer/spec.md`

## Summary

Corrigir a carga AISWEB para interpretar a lista paginada atual, buscar detalhes oficiais por aeródromo e gravar o catálogo somente após validar todos os registros necessários. Persistir a versão individual publicada permite reutilizar detalhes sem novas chamadas quando o registro não mudou. A execução mostra progresso e erros sanitizados; RAB permanece independente.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: requests já existente; `concurrent.futures` da biblioteca padrão para concorrência limitada

**Storage**: PostgreSQL; os campos de versão AISWEB do aeródromo são opcionais para preservar registros legados e obrigatórios para novos registros carregados da fonte

**Testing**: pytest com XML AISWEB fictício, respostas e erros simulados; nenhum teste faz chamadas de rede

**Target Platform**: processo de aplicação/CLI em Linux

**Project Type**: aplicação Flask com comando de carga do catálogo

**Performance Goals**: limitar a quatro chamadas detalhadas simultâneas, informar progresso durante a carga inicial e evitar chamadas detalhadas em atualizações sem mudança de versão

**Constraints**: O endpoint de lista sem filtro retorna registros em vigor e fornece o total; `rowend` define quantidade, não índice final. O endpoint detalhado recebe um ICAO por chamada. Coordenada, elevação, tipo e versão precisam vir da AISWEB; sem completar a carga, não publicar catálogo parcial. Credenciais nunca aparecem em logs. Não adicionar dependências.

**Scale/Scope**: ROTAER corrente, milhares de registros; atualização de `servidor/catalogo.py`, `servidor/modelos.py`, migração Alembic, testes e documentação de operação.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Portão | Resultado |
| --- | --- |
| Especificação antes do servidor | Passa; `spec.md`, plano e tarefas precedem a implementação. |
| Dados oficiais e indisponibilidade explícita | Passa; somente AISWEB fornece posição, elevação e versão; falha não publica carga parcial. |
| Catálogo exige ROTAER vigente | Passa; lista padrão em vigor, sem fallback local para validar plano. |
| Chaves fora do repositório | Passa; usa configuração já existente e omite URLs/credenciais dos erros. |
| PostgreSQL/Alembic e pilha pequena | Passa; migração aditiva e biblioteca padrão para limite de concorrência. |
| Texto em português e cálculos no servidor | Passa; apenas saída do comando de operação muda, cálculos permanecem intactos. |

## Research Summary

Decisões e evidências estão em [research.md](./research.md). Não restam decisões de produto em aberto.

## Design & Contracts

- [data-model.md](./data-model.md): cache de versão por aeródromo e carga atômica.
- [contracts/aisweb-rotaer.md](./contracts/aisweb-rotaer.md): resposta de lista, detalhe e saída operacional.
- [quickstart.md](./quickstart.md): testes isolados e verificação manual da carga.

## Project Structure

### Documentation

```text
specs/014-corrigir-carga-rotaer/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/aisweb-rotaer.md
└── tasks.md
```

### Source Code

```text
servidor/catalogo.py                         # parser, paginação, detalhes, cache e diagnóstico
servidor/modelos.py                          # versão e data AISWEB por aeródromo
alembic/versions/<migration>                 # colunas de versão AISWEB
tests/test_catalogo_aerodromos.py            # regressões de lista, detalhe, cache e falha
documentacao/operacao.md                     # progresso e comportamento da carga
```

**Structure Decision**: Reutilizar o comando de catálogo e os modelos existentes. A carga prepara todos os registros em memória, reutiliza detalhes existentes apenas quando o identificador de versão coincide, e só então grava a nova publicação em uma transação. Não há novo serviço, banco ou pacote.

## Complexity Tracking

Nenhuma violação da constituição. A migração aditiva registra a versão da fonte necessária para evitar milhares de consultas repetidas; `concurrent.futures` já pertence à biblioteca padrão.
