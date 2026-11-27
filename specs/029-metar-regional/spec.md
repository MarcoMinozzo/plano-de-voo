---
description: "Usar METAR regional próximo ao aeródromo e consultar TAF independentemente"
---

# Especificação: METAR regional próximo ao aeródromo

**Feature Branch**: `029-metar-regional`

**Criado**: 2026-11-26

**Status**: Draft

**Entrada**: "Precisamos de um METAR da cidade ou região próxima ao aeroporto; corrija o erro de código." Distância máxima confirmada pelo usuário: 50 NM.

## Cenários de usuário e testes

### História 1 — Consultar meteorologia local ou regional (Prioridade: P1)

Como piloto, quero ver a observação METAR do aeródromo ou, quando não existir, a de uma estação próxima claramente identificada, sem perder um TAF disponível por falta de METAR.

**Prioridade**: A maioria dos aeródromos de escala não publica observação ou previsão própria; uma fonte regional próxima é mais útil que omitir toda a meteorologia, desde que sua origem e distância fiquem explícitas.

**Teste independente**: Consultar planos com METAR direto, apenas METAR regional, TAF sem METAR e nenhum dado em até 50 NM.

**Cenários de aceitação**:

1. **Dado** um METAR válido do próprio aeródromo, **quando** o plano é calculado, **então** esse METAR tem prioridade sobre qualquer estação regional.
2. **Dado** que não exista METAR direto, **quando** houver um METAR válido de estação AWC a até 50 NM, **então** o relatório mostra a estação, indicativo, distância e horário da observação, identificando-o como regional e não como condição do aeródromo.
3. **Dado** que não haja METAR válido a até 50 NM, **quando** o plano é calculado, **então** o METAR aparece indisponível e nenhum dado distante ou inventado é usado.
4. **Dado** que o METAR esteja ausente ou falhe, mas o aeródromo tenha TAF, **quando** o plano é calculado, **então** o TAF é consultado e exibido independentemente.
5. **Dado** que não haja TAF para o próprio aeródromo, **quando** houver ou não METAR regional, **então** o TAF permanece indisponível; uma previsão de outro aeródromo não é atribuída a ele.
6. **Dado** que a consulta ao provedor falhe, **quando** o relatório é montado, **então** os dados afetados aparecem indisponíveis e a falha fica diagnosticável sem expor credenciais.

## Casos extremos

- Coordenadas inválidas do aeródromo ou da estação impedem o cálculo da distância e a seleção regional.
- Um METAR regional exatamente a 50 NM é elegível; um acima de 50 NM não é.
- Se dois METARs tiverem a mesma distância, a seleção é determinística.
- Um resultado regional nunca é apresentado como METAR do aeródromo nem como condição operacional da pista.
- A ausência de METAR não impede a consulta independente do TAF.

## Requisitos

### Requisitos funcionais

- **FR-001**: O sistema MUST preferir o METAR válido publicado para o próprio aeródromo.
- **FR-002**: Sem METAR direto, o sistema MUST selecionar a estação AWC com METAR válido mais próxima, somente quando a distância geográfica até o aeródromo for de no máximo 50 NM.
- **FR-003**: O relatório MUST identificar um resultado substituto como “METAR regional” e apresentar nome e indicativo da estação, distância em NM e horário UTC da observação.
- **FR-004**: O relatório MUST distinguir claramente a estação observadora do aeródromo planejado; não pode sugerir que o METAR regional descreve as condições do aeródromo.
- **FR-005**: A consulta do TAF MUST ser independente da disponibilidade ou falha da consulta METAR e MUST usar somente o indicativo do aeródromo consultado.
- **FR-006**: Sem METAR elegível, TAF do aeródromo ou resposta válida do provedor, cada produto afetado MUST aparecer indisponível; valores não podem ser estimados ou copiados de outra localidade.
- **FR-007**: Falhas de consulta MUST ser registradas de forma útil para diagnóstico sem incluir chaves ou credenciais.
- **FR-008**: Os dados e a identificação da estação que os publicou MUST permanecer associados ao aeródromo e plano correspondentes no relatório.

### Entidades principais

- **Observação METAR**: texto e campos observados, estação publicadora, indicativo, coordenadas, horário UTC e distância ao aeródromo de referência.
- **Previsão TAF**: previsão publicada para o indicativo do aeródromo; disponibilidade independente do METAR.

## Critérios de sucesso

### Resultados mensuráveis

- **SC-001**: Todos os planos com METAR direto mostram esse dado em preferência a qualquer estação próxima.
- **SC-002**: Todo METAR substituto está a até 50 NM e mostra nome, indicativo, distância e horário UTC da estação.
- **SC-003**: Nenhum METAR de estação além de 50 NM ou sem coordenadas válidas é apresentado como substituto.
- **SC-004**: A ausência ou falha do METAR não oculta um TAF válido do aeródromo.
- **SC-005**: Nenhum TAF de outro aeródromo é atribuído ao aeródromo do plano.

## Pressupostos

- A fonte permanece o Aviation Weather Center; não haverá fallback silencioso para outro provedor.
- O limite regional confirmado é 50 NM.
- O TAF é exclusivo do aeródromo consultado; apenas o METAR admite a substituição regional solicitada.
- Ao abrir um plano salvo, METAR e TAF são consultados novamente para a apresentação atual. Essa consulta não grava o resultado no plano nem altera a rota ou os cálculos.
- O aviso didático existente permanece visível; METAR regional não é apresentado como confirmação das condições da pista.
