# Contrato HTTP: rota com escalas

Complementa o contrato do plano direto. Sessão, recusa e isolamento não mudam. Corpo de erro diz o campo ou a fonte que falhou. Não inventa aeródromo, dado técnico, vento nem pôr do sol.

## `GET /aerodromos`

Lista aeródromos de avião da emenda vigente. Exige sessão.

- Sucesso: identificador, nome, fonte da emenda. Sem coordenada no HTML além da que a tela do plano já recebe para desenhar a rota calculada.
- Catálogo indisponível: estado `indisponivel` e nenhum aeródromo apresentado como lista nacional.

## `GET /aeronaves`

Lista modelos de avião pequeno. Exige sessão.

- Sucesso: até 30 modelos completos, com nome, frota, fontes técnicas selecionadas por campo e um indicador `estimativa_didatica`. Cada fonte inclui tipo, publicador, referência, data de publicação/consulta, aplicabilidade e perfil quando necessário; POH/AFM também inclui revisão/edição e página/tabela. Sem peso, velocidade ou consumo neste índice.
- Ordem: filtrar modelos completos, ordenar por frota decrescente e nome canônico crescente em empate, e só então limitar a 30. Modelos incompletos e completos além do limite não aparecem.
- Registro indisponível: estado `indisponivel` e lista `modelos` vazia. Não oferecer modelos locais nem aceitar novos planos com aeronave até carregar um extrato vigente.

## `POST /planos` e `PUT /planos/{id}`

A entrada continua origem, destino, hora, modelo e dados particulares. Não há campo de escala.

- Sucesso aceitável: `rota` com trechos ordenados. Cada trecho tem origem, destino, distância, proa, tempo, combustível, unidade, fonte, estado do vento e estado do pôr do sol. Grandezas derivadas identificam as fontes dos valores técnicos de entrada; dados secundários carregam `estimativa_didatica: true`. A rota inclui `criterio` com o texto "menor tempo de voo" e a hipótese de reabastecimento com a fonte técnica selecionada.
- Sucesso inaceitável: o plano é gravado, `estado` é `inaceitavel`, e `motivo` diz o limite ou a fonte que impediu a rota.
- Erro sem gravação: origem igual ao destino, lugar fora da emenda, heliponto, modelo incompleto ou fora da seleção vigente do MVP, fonte, data ou aplicabilidade técnica não verificável, perfil nominal pareado ausente, combustível utilizável ausente, catálogo RAB indisponível, catálogo nacional de aeródromos indisponível ou dado particular ausente.

## `GET /planos/{id}` e `GET /planos/{id}/pdf`

Devolvem a mesma rota e as fontes dos valores exibidos. O PDF identifica cada estimativa secundária como didática, inclui as fontes, os trechos, a hipótese de reabastecimento e o aviso de que o resultado não é adequado para voo real e não autoriza o voo. Plano de outro piloto continua recusado, sem revelar se existe.
