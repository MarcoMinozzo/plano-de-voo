# Contrato — Tiles OpenAIP

## Requisição da aplicação

`GET /planos/{plano_id}/camadas/openaip/{z}/{x}/{y}.png`

- Exige sessão autenticada.
- O plano deve pertencer ao piloto da sessão; plano inexistente ou de outro
  piloto retorna `404`.
- `z`, `x` e `y` devem ser inteiros de tile válidos; `z` permitido é de 2 a
  18 e `x`/`y` devem estar dentro da matriz de tiles do zoom.
- A aplicação usa um host OpenAIP fixo e o layer combinado `openaip`.
- A chave é enviada ao provedor pelo header `x-openaip-api-key`; nunca é
  incluída na URL pública, resposta HTML, mensagem de erro ou log.

## Respostas

- `200 image/png`: tile válido do provedor.
- `400`: coordenadas fora dos limites definidos.
- `404`: plano inexistente ou não pertencente ao piloto.
- `503`: chave ausente, autorização recusada, timeout, limite de uso ou falha
  do provedor; corpo contém somente mensagem genérica de indisponibilidade.
- `502`: resposta upstream inválida, tipo de conteúdo inesperado ou tile
  malformado.

As respostas de erro não contêm detalhes da chave nem da URL autenticada.
Diretivas de cache do provedor podem ser respeitadas; não criar retenção local
ou resposta de imagem artificial.

## Interface do mapa

- Ruas é a base inicial.
- OpenAIP é selecionável como uma base distinta e só carrega tiles após seleção.
- Se o mapa estiver abaixo do zoom mínimo 2, a seleção é recusada com aviso;
  não alterar o zoom automaticamente.
- Exibir atribuição visível com link para `https://www.openaip.net` enquanto
  OpenAIP estiver selecionada.
- Exibir “OpenAIP — dados aeronáuticos comunitários; não é carta WAC nem fonte
  oficial”.
- Falha de tile remove ou desativa OpenAIP e informa indisponibilidade sem
  mudar silenciosamente para ruas ou carta AISWEB.
- Radar inicia desligado e sua seleção é independente da base.
