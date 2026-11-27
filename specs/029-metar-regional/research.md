# Pesquisa: METAR regional próximo ao aeródromo

## API AWC

- **Decisão**: Usar a API pública do Aviation Weather Center para observações METAR por indicativo ou por caixa geográfica.
- **Evidência**: O OpenAPI oficial descreve `/api/data/metar` como observações decodificadas e aceita `ids` ou `bbox`; os campos JSON incluem indicativo, nome, latitude, longitude, horário e texto bruto. A especificação do parâmetro `bbox` define a ordem `(lat0, lon0, lat1, lon1)` e o máximo de três casas decimais.
- **Motivo**: AWC é a fonte já usada pelo produto e os próprios registros fornecem posição e identidade da estação, necessários para não atribuir o METAR regional ao aeroporto errado.
- **Referências**:
  - [Documentação da Data API AWC](https://aviationweather.gov/data/api/)
  - [OpenAPI AWC](https://aviationweather.gov/data/schema/openapi.yaml)

## Disponibilidade observada

- **Evidência em 2026-11-26**: A consulta do plano 5 retornou METAR e TAF de SBBU. Consultas atuais por SDFD e SBEK retornaram sem METAR e `[]` para TAF. Portanto, a ausência em aeródromos pequenos é de cobertura/publicação, não uma indicação de que todos os indicativos da rota tenham boletins.
- **Decisão**: Se a estação do aeródromo não reportar, procurar observações AWC próximas. A busca regional não deve fabricar uma observação nem aceitar estação a mais de 50 NM.
- **Referências**:
  - [METAR de SBBU](https://aviationweather.gov/api/data/metar?ids=SBBU&format=json)
  - [TAF de SBBU](https://aviationweather.gov/api/data/taf?ids=SBBU&format=json)
  - [METAR de SDFD](https://aviationweather.gov/api/data/metar?ids=SDFD&format=json)
  - [TAF de SDFD](https://aviationweather.gov/api/data/taf?ids=SDFD&format=json)
  - [METAR de SBEK](https://aviationweather.gov/api/data/metar?ids=SBEK&format=json)
  - [TAF de SBEK](https://aviationweather.gov/api/data/taf?ids=SBEK&format=json)

## Defeito de independência METAR/TAF

- **Decisão**: Tentar cada produto isoladamente. Uma resposta vazia ou falha METAR não deve retornar antes da solicitação TAF.
- **Evidência**: Em `servidor/tempo.py`, a função atual retorna indisponibilidade quando METAR é `204`, vazio ou inexistente antes de executar a solicitação TAF. O segundo `try` só é alcançado quando há METAR.
- **Alternativas rejeitadas**: Associar o TAF de outra estação ao aeroporto; isso atribuiria uma previsão terminal a uma localidade diferente.

## Distância e armazenamento

- **Decisão**: Formar uma caixa AWC de busca em torno das coordenadas ROTAER e calcular a distância geodésica exata em milhas náuticas para filtrar, ordenar e desempatar. Salvar indicativo/nome/horário/distância na estrutura JSON meteorológica existente.
- **Motivo**: A caixa reduz o conjunto consultado; o cálculo exato preserva o limite de 50 NM, e o JSON atual já guarda os boletins do plano sem uma segunda fonte de verdade.
- **Alternativas rejeitadas**: Selecionar pelo centro da caixa, que não assegura o raio de 50 NM; escolher a primeira resposta da API, que não garante ser a mais próxima.
- **Dependências**: `math` e `requests` da biblioteca/stack já instalada; sem dependências novas.
