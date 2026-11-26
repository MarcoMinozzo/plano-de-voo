# Contrato operacional AISWEB ROTAER

## Lista em vigor

- Consulta: área `rotaer`, filtro de tipo `AD`, paginação com `rowstart` e quantidade `rowend`.
- O parâmetro `amdt` fica ausente para obter a lista atualmente em vigor; `last_amdt` limita a consulta aos registros que entraram em vigor naquela emenda.
- Resposta: XML com raiz `aisweb`, contêiner `rotaer` e atributo `total`; cada `item` informa pelo menos `id`, `type`, `AeroCode`, `name` e `dt`.
- `id` é a versão individual publicada; `dt` é a data de publicação/atualização do registro.

## Detalhes

- Consulta: área `rotaer` e um `icaoCode` por solicitação.
- Campos obrigatórios: ICAO correspondente, tipo de aeródromo de avião, latitude, longitude e `altM`.
- A resposta não pode ser reaproveitada para outro ICAO.
- Detalhes persistidos só podem ser reutilizados quando versão e data da lista coincidirem com o registro local.
- Se a resposta XML não identificar o ICAO solicitado, consultar a mesma área com `force=html`, conforme o modo oficial documentado pelo AISWEB. Só aceitar o retorno quando o código, tipo, data da emenda, coordenadas e elevação puderem ser validados; uma resposta HTML vazia ou incompleta mantém o catálogo indisponível.

## Resultado do comando de carga

- Progresso da lista e dos detalhes é apresentado sem URL completa nem credenciais.
- O estado final ROTAER é `disponivel` somente após concluir e persistir todos os registros.
- Falha de rede, XML, paginação ou detalhe informa categoria/ICAO/campo sem expor parâmetros secretos e termina com estado `indisponivel`.
- A carga do RAB continua sendo executada independentemente do resultado ROTAER.
