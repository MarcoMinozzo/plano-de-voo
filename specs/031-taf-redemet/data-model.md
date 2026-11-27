# Data Model: Priorizar TAF da REDEMET

## Entidades existentes utilizadas

### Boletim de aeródromo

`meteorologia.aerodromos[ICAO]` mantém METAR e TAF independentes e associados ao indicativo consultado.

### Observação TAF

Campos já usados:

- `raw`: texto original publicado.
- `fonte`: fonte efetivamente usada (`REDEMET` ou `Aviation Weather Center`).
- `hora`: horário de recebimento/emissão fornecido pela fonte.
- `estado`: opcional; quando `indisponivel`, nenhum texto TAF deve ser exibido.

Metadados REDEMET adicionais no JSON:

- `icao`: indicativo publicado, validado contra o aeródromo consultado.
- `validade_inicial`: início da validade fornecido pela REDEMET.
- `validade_final`: fim da validade fornecido pela REDEMET.

## Validações e transições

- Preferência: REDEMET utilizável → AWC utilizável para o mesmo ICAO → indisponível.
- Mensagens repetidas: escolher a de maior `recebimento` entre entradas válidas.
- TAF sem mensagem, localidade correspondente ou horários válidos é rejeitado e aciona o fallback.
- Uma falha TAF não altera o objeto METAR do boletim.
- O resultado em GET é transitório; não grava no plano.
- O snapshot gravado ao criar/editar um plano mantém compatibilidade com registros antigos, que podem não ter os metadados novos.
