# Contrato — Imagem de satélite no mapa

## Endpoint da aplicação

`GET /planos/{plano_id}/camadas/satelite`

- Exige sessão autenticada e propriedade do plano pelo piloto.
- A consulta à REDEMET ocorre somente após o usuário ativar Satélite.
- Não grava resposta no plano nem retorna a chave de serviço.

### Resposta disponível

```json
{
  "estado": "disponivel",
  "provedor": "REDEMET",
  "fonte": "REDEMET Satélite realçada",
  "hora_frame": "2026-05-10 23:00:00",
  "imagem_url": "https://estatico-redemet.decea.mil.br/satelite/.../realcada_202605102300.png",
  "bounds": {
    "lat_min": -56.0,
    "lat_max": 12.52,
    "lon_min": -100.0,
    "lon_max": -25.24
  }
}
```

Valores são ilustrativos; o sistema usa somente campos válidos recebidos da API.

### Indisponibilidade e acesso

- Fonte sem chave, indisponível, vazia ou malformada: HTTP 200 com `{"estado":"indisponivel"}`; não incluir URL, chave ou exceção interna.
- Sem autenticação: resposta padrão de acesso não autenticado.
- Plano inexistente ou pertencente a outro piloto: HTTP 404 com a mensagem padrão de recusa.

## Validação do frame

- URL precisa usar HTTPS e o host oficial `estatico-redemet.decea.mil.br`.
- Data/hora deve ser texto não vazio recebido da fonte.
- Limites precisam ser números finitos válidos e respeitar `lat_min < lat_max` e `lon_min < lon_max`.
- Em resposta inválida, a interface não cria overlay e anuncia indisponibilidade.

## Interface do mapa

- Satélite começa desligado, é um overlay independente de Radar de chuva e pode coexistir com ele.
- A rota permanece acima das imagens.
- WAC continua sendo documento AISWEB, não tile raster; se indisponível, controle visível/desabilitado com mensagem acessível.
