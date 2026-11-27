# Contrato: Seleção de TAF por aeródromo

## Resultado por aeródromo

`meteorologia.aerodromos[ICAO].taf` permanece `null`, indisponível ou um objeto com:

```json
{
  "raw": "TAF SBMT ...",
  "fonte": "REDEMET",
  "hora": "2026-11-27 04:20:08",
  "icao": "SBMT",
  "validade_inicial": "2026-11-27 06:00:00",
  "validade_final": "2026-11-27 18:00:00"
}
```

Os horários são fornecidos pela origem em UTC. A mensagem bruta é preservada; metadados ausentes não são inventados.

## Ordem de seleção

1. Consultar TAF REDEMET pelo indicativo ICAO do próprio aeródromo.
2. Se a resposta não contiver mensagem válida para o mesmo indicativo, consultar TAF AWC pelo mesmo indicativo.
3. Se nenhuma fonte fornecer mensagem válida, retornar TAF indisponível.

## Requisitos de segurança e isolamento

- A chave REDEMET fica apenas no servidor.
- Respostas de HTML/JSON e logs não incluem a chave nem a URL de consulta com credenciais.
- Nenhum TAF de outro indicativo é associado ao aeródromo solicitado.
- Falha TAF é independente de METAR e das consultas a outros aeródromos.
