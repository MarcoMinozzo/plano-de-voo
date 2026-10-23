# Contrato HTTP: rota com escalas

Complementa o contrato do plano direto. Sessão, recusa e isolamento não mudam. Corpo de erro diz o campo ou a fonte que falhou. Não inventa aeródromo, manual, vento nem pôr do sol.

## `GET /aerodromos`

Lista aeródromos de avião da emenda vigente. Exige sessão.

- Sucesso: identificador, nome, fonte da emenda. Sem coordenada no HTML além da que a tela do plano já recebe para desenhar a rota calculada.
- Catálogo indisponível: estado `indisponivel` e nenhum aeródromo apresentado como lista nacional.

## `GET /aeronaves`

Lista modelos de avião pequeno. Exige sessão.

- Sucesso: nome, frota, `manual_estado`, e a fonte do manual quando `gravado`. Sem peso, velocidade ou consumo neste índice.
- Ordem: frota decrescente.
- Registro indisponível: estado `indisponivel`. O Cessna 140 já gravado pode aparecer, sem ser descrito como o registro nacional inteiro.

## `POST /planos` e `PUT /planos/{id}`

A entrada continua origem, destino, hora, modelo e dados particulares. Não há campo de escala.

- Sucesso aceitável: `rota` com trechos ordenados. Cada trecho tem origem, destino, distância, proa, tempo, combustível, unidade, fonte, estado do vento e estado do pôr do sol. A rota inclui `criterio` com o texto "menor tempo de voo" e a hipótese de reabastecimento com a fonte do manual.
- Sucesso inaceitável: o plano é gravado, `estado` é `inaceitavel`, e `motivo` diz o limite ou a fonte que impediu a rota.
- Erro sem gravação: origem igual ao destino, lugar fora da emenda, heliponto, modelo sem manual, catálogo nacional indisponível, dado particular ausente.

## `GET /planos/{id}` e `GET /planos/{id}/pdf`

Devolvem a mesma rota. O PDF inclui os trechos, a hipótese de reabastecimento e o aviso de que não autoriza o voo. Plano de outro piloto continua recusado, sem revelar se existe.
