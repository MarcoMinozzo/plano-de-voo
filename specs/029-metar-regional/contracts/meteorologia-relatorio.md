# Contrato: METAR regional e TAF independente

## Resultado por aeródromo

`meteorologia.aerodromos[ICAO]` representa o aeródromo consultado e contém estado agregado, `metar` e `taf` independentes.

- METAR direto: `regional: false`; indicativo da estação permanece no campo `icao`.
- METAR regional: `regional: true`; contém indicativo/nome da estação, aeródromo de referência, distância NM e horário UTC.
- METAR sem dados elegíveis: estado indisponível, sem texto ou campos meteorológicos inventados.
- TAF: somente o produto retornado para o próprio indicativo consultado; não usar TAF vizinho.
- Resposta do agregado fica disponível quando ao menos um dos dois produtos estiver disponível.
- Abrir um plano salvo consulta METAR/TAF novamente para a apresentação da requisição; não grava essa resposta no JSON do plano nem recalcula rota ou resultados.

## Interface HTML e PDF

- METAR direto continua identificado como METAR do aeródromo.
- METAR regional usa rótulo explícito “METAR regional” e mostra nome/ICAO da estação, distância até o aeródromo de referência e horário UTC.
- Campos e texto bruto vêm da mesma observação regional; não misturar campos de estações diferentes.
- TAF mantém identificação do aeródromo para o qual foi emitido e aparece mesmo se METAR estiver indisponível.
- O modal de fontes e o apêndice PDF relacionam o campo ao AWC e identificam a estação real do METAR.
- Aviso didático permanece. Nenhum dado regional pode sugerir condição confirmada da pista ou autorizar operação.

## Falhas

- Resposta vazia/204 significa produto sem publicação disponível.
- HTTP, rede ou JSON inválido são registrados para diagnóstico sem credenciais e deixam somente o produto afetado indisponível.
- Uma falha METAR não impede uma tentativa TAF; uma falha TAF não apaga o METAR.
