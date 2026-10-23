# Data model: Rota com escalas

Banco: PostgreSQL 16, o mesmo do plano direto. Número de manual existe uma vez no modelo. Coordenada de aeródromo existe uma vez, vinda da emenda.

## EmendaRotaer

A publicação carregada.

| Campo | Regra |
| --- | --- |
| id | Identificador interno |
| codigo_emenda | Obrigatório. Identificador publicado da emenda |
| vigente | No máximo uma emenda vigente |
| carregada_em | Obrigatório |
| estado | `disponivel` ou `indisponivel` |

Sem emenda `disponivel`, o catálogo nacional não alimenta plano novo.

## Aerodromo

Estende o aeródromo já existente. Os sete indicativos antigos podem continuar gravados, mas não contam como catálogo nacional.

| Campo | Regra |
| --- | --- |
| identificador | Obrigatório. O código publicado, inclusive com dígito. Chave. |
| nome | Obrigatório |
| tipo | `aerodromo` ou `heliponto`. Só `aerodromo` entra em origem, destino e escala |
| lat, lon | Obrigatórios quando o tipo é `aerodromo` e a emenda está disponível. Vêm da publicação |
| elev_m | Obrigatória na mesma condição |
| emenda_id | Obrigatória para registro vindo do ROTAER |
| fonte | Obrigatória. Cita a emenda |

Heliponto pode ser gravado para o teste provar que ele não entra na rota. Não é oferecido ao piloto.

## ModeloAviao

O avião pequeno. O registro antigo `Aeronave` do Cessna 140 passa a ser o manual deste modelo, sem segunda cópia dos números.

| Campo | Regra |
| --- | --- |
| nome | Obrigatório. Como o extrato do RAB nomeia o modelo |
| frota | Obrigatória. Quantidade de aeronaves no extrato usado |
| peso_max_decolagem_kg | Obrigatório para classificar o porte. Acima de 5.670 kg não entra |
| manual_estado | `gravado` ou `ausente` |
| fonte_manual | Obrigatória quando `gravado`. Cita o manual oficial |
| velocidade, consumo, combustível de planejamento, pesos e bagagem | Obrigatórios só quando o manual está `gravado`. Uma vez, neste registro |

## ExtratoRab

| Campo | Regra |
| --- | --- |
| id | Identificador interno |
| referencia | Obrigatória. Qual extrato público foi lido |
| carregado_em | Obrigatório |
| estado | `disponivel` ou `indisponivel` |

## Trecho

Perna calculada. Não é editada pelo piloto.

| Campo | Regra |
| --- | --- |
| plano_id | Obrigatório |
| ordem | Obrigatória, a partir de 1 |
| origem_id, destino_id | Obrigatórios, aeródromos de avião |
| distancia, proa, tempo, combustivel | Obrigatórios, com unidade e fonte |
| vento_estado | `disponivel` ou `indisponivel` |
| por_do_sol_estado | `disponivel` ou `indisponivel` |

## Plano

Além dos campos já gravados, o plano guarda `rota_estado` (`aceitavel` ou `inaceitavel`), o motivo quando for inaceitável, e a frase da hipótese de reabastecimento com a fonte do manual. `origem` e `destino` continuam sendo o primeiro e o último aeródromo da rota.

Apagar o plano apaga os trechos. Outro piloto não lê a rota.
