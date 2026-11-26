# Implementation Plan: Auditoria de funções, botões e camadas

**Branch**: `main` | **Date**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/019-auditoria-funcoes-botoes/spec.md`

## Summary

Dar confirmação de sucesso ao salvamento do nome somente após o commit, corrigir os motivos comunicados para radar indisponível e conter a tabela de fontes em telas estreitas. Auditar os demais controles primários por testes e navegação não destrutiva. A WAC, OpenAIP e radar continuam obedecendo aos gates de fonte, chave, licença e georreferenciamento; nenhuma camada será ativada apenas para parecer funcional.

## Technical Context

**Language/Version**: Python 3.10+; Jinja, HTML, CSS e JavaScript existentes.

**Primary Dependencies**: Flask e Leaflet já instalados; nenhuma dependência nova.

**Storage**: PostgreSQL existente; sem migração ou alteração do esquema. O nome atual é mantido em `Piloto.nome_exibicao`; o JSON já usado para radar poderá receber campo opcional `motivo`.

**Testing**: pytest focado em `tests/test_acesso.py`, `tests/test_tela_piloto.py` e `tests/test_tempo.py`; verificação manual no navegador em 390 px e 1440 px. A suíte completa atual teve 137 aprovações e uma falha de complexidade em `servidor/pdf_plano.py`; não é escopo desta feature.

**Target Platform**: Aplicação web Flask em navegadores móveis e desktop.

**Project Type**: Aplicação web monolítica.

**Performance Goals**: Não adicionar chamadas externas ao salvar o perfil nem bloquear a abertura do plano.

**Constraints**: Preservar isolamento do piloto, cálculos, sessão e conteúdo didático; não expor segredos nem executar gravações de auditoria em dados reais. Indisponibilidade deve refletir o motivo conhecido sem revelar detalhes internos de exceções. Manter a WAC bloqueada até cumprir seus gates.

**Scale/Scope**: Fluxos de perfil, mapa/plano e navegação principal; sem mudança de dados persistidos além do campo opcional já contido no JSON de radar.

## Constitution Check

| Princípio | Estado | Salvaguarda |
|---|---|---|
| I. Especificação antes do código | PASS | Spec, plano e tarefas são concluídos antes de alterar servidor ou templates. |
| II. Limite educacional | PASS | Preservar avisos existentes; não apresentar mapa ou camada como autorização de voo. |
| III. Cálculo no servidor | PASS | Nenhuma fórmula ou cálculo de rota será movido ao navegador. |
| IV. Unidades, fonte e indisponibilidade | PASS | Mostrar indisponibilidade real; não inventar dados nem promover uma fonte a carta oficial. |
| V. Pilha pequena e banco relacional | PASS | Reusar Flask/PostgreSQL e JSON existente; sem nova dependência, banco ou migração; segredos permanecem fora do repositório. |
| Isolamento por piloto | PASS | Testes de perfil mantêm a verificação do piloto autenticado. |

Nenhuma violação constitucional identificada.

## Project Structure

```text
app.py
servidor/
├── tempo.py
└── openaip.py
templates/
├── perfil.html
└── plano.html
tests/
├── test_acesso.py
├── test_tela_piloto.py
├── test_tempo.py
└── test_rota_pdf.py
documentacao/piloto.md
specs/019-auditoria-funcoes-botoes/
```

**Structure Decision**: Reutilizar a aplicação Flask/Jinja, o JSON existente de disponibilidade e os testes por cliente de aplicação. Criar apenas artefatos de especificação; não introduzir serviço ou camada persistente.

## Phase 0: Outline & Research

Ver decisões e evidências em [research.md](./research.md). Os fatos de código e os gates do mapa estão determinados; não há dependência externa nova nem questão de tecnologia pendente.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md): documentar uso de campos existentes e o `motivo` opcional no estado JSON de radar; nenhuma migração.
- [contracts/acoes-e-indisponibilidade.md](./contracts/acoes-e-indisponibilidade.md): registrar estados de perfil e das camadas apresentados ao piloto.
- [quickstart.md](./quickstart.md): fornecer testes isolados e validação visual responsiva não destrutiva.
- Constituição reavaliada após o desenho: PASS; nenhum cálculo client-side, fallback enganoso, dado inventado ou chave no repositório.

## Complexity Tracking

Sem violações ou abstrações adicionais a justificar.
