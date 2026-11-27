# Modelo de dados: METAR regional próximo ao aeródromo

## Estruturas existentes

### Aeródromo

Usa indicativo, nome e coordenadas verificadas do ROTAER. Coordenadas ausentes ou inválidas impedem busca regional. Nenhuma coluna nova é necessária.

### Meteorologia salva no plano

Os boletins do cálculo permanecem no JSON existente do plano, associados ao indicativo de cada aeródromo. Ao abrir o plano, METAR e TAF são consultados novamente e usados somente na resposta daquela página; essa atualização não sobrescreve o JSON persistido nem altera rota ou cálculos. O status do agregado é disponível se pelo menos METAR ou TAF estiver disponível; cada produto mantém seu próprio status.

## Dados derivados

### METAR

- `raw`: relatório bruto AWC.
- `hora`: horário de observação UTC.
- `icao`: indicativo da estação que produziu o relatório.
- `nome_estacao`: nome do ponto de observação fornecido pelo AWC.
- `regional`: booleano que diferencia observação do próprio aeródromo de observação próxima.
- `aerodromo_referencia`: indicativo ROTAER ao qual o relatório regional foi associado.
- `distancia_nm`: distância não arredondada em milhas náuticas para comparação; apresentação arredonda para uma casa decimal.
- Campos meteorológicos já decodificados, unidades e `fonte` permanecem conforme o contrato atual.

Para METAR direto, `regional` é falso e não há distância substituta. Para regional, `icao` identifica sempre a estação publicadora, não o aeródromo de referência.

### TAF

Mantém `raw`, `hora` e `fonte`, consultados exclusivamente pelo indicativo do aeródromo. A ausência de METAR não altera a disponibilidade do TAF.

## Regras

- Um METAR direto válido prevalece sobre todos os regionais.
- Sem METAR direto, considerar apenas registros com texto, coordenadas e indicativo válidos.
- A distância é calculada em grande-círculo e comparada sem arredondamento; `<= 50 NM` é elegível.
- Ordenação determinística: distância exata crescente e, em empate, indicativo crescente.
- Sem resultado elegível, `metar` fica indisponível; não reutilizar dado de outro plano ou horário.
- Falha de um produto não remove o outro.
- Ao abrir um plano salvo, atualizar METAR/TAF apenas para a resposta atual; não persistir a atualização. Não consultar AWC por simples troca de abas.
