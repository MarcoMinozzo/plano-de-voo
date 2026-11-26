# Research — Camada aeronáutica OpenAIP

## Decisão

- Usar o layer combinado PNG `openaip` como uma base selecionável, não como
  overlay transparente sobre ruas. O endpoint oficial descreve os PNG como
  tiles TMS e recomenda o layer combinado.
- Não rotular OpenAIP como carta WAC, fonte oficial ou garantia de navegação.
  A carta visual oficial continua sendo AISWEB, sujeita aos gates existentes.
- Buscar os tiles pelo servidor autenticado da aplicação, enviando a chave
  no header `x-openaip-api-key`. A chave não é enviada ao navegador.
- A camada só inicia por ação explícita do piloto. O mapa de ruas permanece
  inicial e o radar continua independente.
- Não guardar tiles em banco nem em cache próprio nesta etapa. Se o provedor
  enviar cabeçalhos de cache, respeitá-los; não inventar prazo de retenção.

## Evidência oficial

- A [documentação oficial da API de tiles OpenAIP](https://docs.openaip.net/?urls.primaryName=Tiles%20API)
  confirma autenticação por `x-openaip-api-key` ou query, recomenda manter
  chaves confidenciais, e descreve o layer combinado `openaip`.
- O schema oficial
  [Tiles API OpenAPI](https://api.tiles.openaip.net/api/system/specs/v1/schema.json)
  informa o endpoint PNG
  `https://api.tiles.openaip.net/api/data/openaip/{z}/{x}/{y}.png`, que é TMS;
  Leaflet precisa respeitar a orientação TMS. O serviço anuncia zoom mínimo 2
  e recomenda cache responsável em razão de rate limits.
- O mesmo schema requer atribuição a [OpenAIP](https://www.openaip.net) e
  declara licença Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
- A [licença CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
  limita o uso a fins não comerciais e exige atribuição.

## Alternativas consideradas

- **Colocar a chave no URL enviado ao Leaflet**: rejeitado porque a chave
  ficaria visível no navegador e nas ferramentas de rede.
- **Desenhar PNG OpenAIP sobre a base de ruas**: rejeitado porque o serviço
  documenta o PNG como layer combinado com base cartográfica; ele será uma
  opção de base própria.
- **Usar OpenAIP como substituto da WAC AISWEB**: rejeitado porque os dados não
  são uma carta WAC nem fonte oficial.
- **Persistir cache de tiles no servidor**: adiado; não é necessário para a
  primeira integração e exigiria definir armazenamento, validade e operação.

## Consequências

- Sem chave, licença aplicável ou resposta válida, a camada fica indisponível
  com mensagem explícita; outras bases não são trocadas automaticamente.
- O acesso a cada tile verifica sessão e propriedade do plano. O servidor só
  faz requisições ao host e caminho de tiles OpenAIP documentados e valida os
  índices de tile.
- Testes usam respostas simuladas e nunca dependem de chave ou acesso externo.
