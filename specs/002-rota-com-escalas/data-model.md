# Data model: Rota com escalas

Banco: PostgreSQL 16, o mesmo do plano direto. Valores técnicos selecionados continuam nos campos de `Aeronave`; sua procedência fica registrada por campo e por fonte. Coordenada de aeródromo existe uma vez, vinda da emenda.

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

O modelo de avião pequeno conforme o extrato vigente do RAB. Cada registro representa um nome canônico desse extrato e segue a mesma regra de manual e completude, sem exceção por modelo.

| Campo | Regra |
| --- | --- |
| nome | Obrigatório. Nome canônico exatamente como o extrato do RAB identifica o modelo |
| frota | Obrigatória. Quantidade de aeronaves no extrato usado |
| peso_max_decolagem_kg | Obrigatório para classificar o porte. Acima de 5.670 kg não entra |
| manual_estado | `gravado` somente após conferência humana de todos os dados obrigatórios e das fontes aplicáveis, oficiais ou secundárias; caso contrário `ausente`. Não indica validade operacional |
| fonte_manual | Campo legado mantido para compatibilidade; não comprova completude nem substitui as fontes por campo |
| velocidade e consumo nominais de cruzeiro, combustível utilizável, pesos e limites de bagagem | Valores selecionados usados no cálculo. Cada campo obrigatório precisa de fonte correspondente em `FonteTecnicaAeronave`; velocidade e consumo devem referir-se ao mesmo perfil nominal. O combustível é utilizável, não a capacidade total dos tanques |

O nome canônico do RAB não basta para provar aplicabilidade técnica. Cada fonte declara o modelo/variante a que se aplica; fabricante, PMD, substring ou unicidade de um candidato não autorizam transferir valores. A fonte mais recente aplicável seleciona o valor; em empate de data ou sem data/aplicabilidade verificável, o campo fica indisponível.

## FonteTecnicaAeronave

Uma linha registra a alegação de uma fonte para um campo técnico de um modelo. As fontes concorrentes permanecem registradas para auditoria, mesmo quando não forem selecionadas.

| Campo | Regra |
| --- | --- |
| aeronave_id | Obrigatório; liga a fonte ao modelo de avião |
| campo | Obrigatório; nome do valor técnico documentado |
| valor, unidade | Obrigatórios; valor publicado sem conversão destrutiva e unidade explícita |
| tipo_fonte | `oficial` ou `secundaria` |
| publicador | Obrigatório |
| referencia | Obrigatória; URL ou identificação bibliográfica/documental precisa |
| data_publicacao | Obrigatória e verificável; usada para priorizar fontes conflitantes |
| data_consulta | Obrigatória; registra quando a referência foi conferida |
| modelo_variante | Obrigatório; aplicabilidade declarada pela fonte |
| perfil | Obrigatório para velocidade e consumo; deve permitir confirmar que formam um par |
| revisao_edicao, pagina_tabela | Obrigatórios quando a referência é POH/AFM |
| selecionada | No máximo uma fonte por campo; seu valor deve coincidir com o campo correspondente em `Aeronave` |
| divergencia | Registra valores conflitantes e a incerteza; não combina nem calcula média |

Uma fonte secundária selecionada deve ser marcada como estimativa didática em toda apresentação. Proveniência selecionada não certifica validade operacional.

### Dados usados por trecho

| Dado | Unidade armazenada | Regra |
| --- | --- | --- |
| Velocidade nominal de cruzeiro | `kt` | Mesmo perfil e condição de potência/altitude do consumo |
| Consumo nominal de cruzeiro | `gal/h` | Mesmo perfil da velocidade |
| Combustível utilizável | `gal` | Exclui a parcela inutilizável; nunca usar capacidade total como combustível disponível |
| Peso vazio, peso máximo de decolagem e bagagem máxima | `kg` | Valores e referências do POH/AFM aplicável |
| Fonte de cada valor | referência estruturada | Publicador, referência, data de publicação e consulta, aplicabilidade e perfil quando necessário; revisão/edição e página/tabela para POH/AFM |

Um modelo só é completo para o cálculo quando combustível utilizável, velocidade e consumo do mesmo perfil nominal, peso vazio, peso máximo de decolagem e limite de bagagem têm valor e uma fonte selecionada com unidade, publicador, referência, data e aplicabilidade verificáveis. A elegibilidade é derivada desses dados e de `manual_estado="gravado"`; não cria um segundo estado persistido.

Com extrato vigente, o seletor ordena primeiro por frota decrescente e, em empate, pelo nome canônico crescente; filtra os modelos completos e oferece no máximo os primeiros 30. Modelos incompletos ou além do limite ficam em espera, não aparecem e não podem ser aceitos em `POST` ou `PUT`. Sem extrato vigente, o seletor fica indisponível e vazio; não usa modelos locais como fallback.

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
| distancia, proa, tempo, combustivel | Obrigatórios, com unidade e fonte; resultados derivados apontam às fontes dos valores técnicos de entrada |
| vento_estado | `disponivel` ou `indisponivel` |
| por_do_sol_estado | `disponivel` ou `indisponivel` |

## Plano

Além dos campos já gravados, o plano guarda `rota_estado` (`aceitavel` ou `inaceitavel`), o motivo quando for inaceitável, e a frase da hipótese de reabastecimento com a fonte técnica selecionada. `origem` e `destino` continuam sendo o primeiro e o último aeródromo da rota.

Apagar o plano apaga os trechos. Outro piloto não lê a rota.
