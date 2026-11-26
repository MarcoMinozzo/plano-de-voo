# Research: Camada suplementar de radar RainViewer

## Decisão: usar RainViewer como camada opcional separada

**Rationale**: O usuário escolheu acrescentar RainViewer como camada suplementar, sem substituir a REDEMET. A API pública documenta frames de radar e tiles de cobertura sem exigir chave; os termos permitem uso educacional com atribuição visível, compatível com a finalidade atual do produto. A integração deve permanecer desligada até ação explícita e comunicar que a fonte é não oficial.

**Alternatives considered**:

- **REDEMET como fallback automático**: rejeitado. A constituição exige REDEMET como fonte oficial, e a camada RainViewer deve ser distinta, sem substituir nem esconder o estado da fonte oficial.
- **Integração direta com o portal SOS Chuva/INPE**: mantida como alternativa futura. O portal oficial apresenta 12 estações e dados CAPPI, e o Governo Federal descreve acesso gratuito a produtos de radar do INPE. As páginas consultadas não definem um contrato público de tiles/API estável adequado para esta integração.
- **Visual Crossing**: não selecionado. A documentação consultada é ambígua quanto ao acesso sem chave: a introdução menciona acesso anônimo, mas os detalhes do endpoint identificam chave como parâmetro requerido. O produto também é um composto de precipitação, não um feed de radar estritamente identificado.

## Fatos verificados

- A [documentação Weather Maps da RainViewer](https://www.rainviewer.com/api/weather-maps-api.html) define o manifesto público em `https://api.rainviewer.com/public/weather-maps.json`. A documentação atual descreve frames passados por até duas horas, em intervalos de dez minutos; o `time` de cada frame é separado do horário de geração do manifesto.
- A mesma documentação apresenta tiles de radar, limite de zoom nativo 7 e tiles de máscara de cobertura. A máscara marca cobertura e áreas sem cobertura, mas a RainViewer avisa que ela não é atualizada frequentemente. O endpoint separado de banco de radares está explicitamente [depreciado](https://www.rainviewer.com/api/database.html).
- Os [termos da API](https://www.rainviewer.com/api.html) limitam o serviço público gratuito a uso pessoal, educacional e comunitário em pequena escala, exigem crédito visível com link e não garantem disponibilidade ou cobertura. A página informa que não é necessária chave ou cadastro para os endpoints públicos atuais e recomenda cache.
- A [lista de fontes brasileiras da RainViewer](https://www.rainviewer.com/radars/brazil.html) inclui REDEMET/DATEMET, STARNET/USP, IPMET/UNESP, SIMEPAR, INEA, FUNCEME, CEMADEN e outras redes. Portanto, RainViewer agrega fontes; não deve ser descrita como observação independente nem cobertura nacional garantida.
- O [SOS Chuva do CPTEC/INPE](https://satelite.cptec.inpe.br/soschuvaapp/) anuncia radar CAPPI e doze estações. A página de [serviço do Governo Federal](https://www.gov.br/pt-br/servicos/acessar-gratuitamente-dados-e-produtos-derivados-de-satelites-radares-e-instrumentos-meteorologicos-correlatos) descreve acesso gratuito a imagens e dados de radar do INPE. O catálogo de [produtos CAPPI do INPE](https://data.inpe.br/dados/radares-meteorologicos/) descreve resolução horizontal de 1 km e aquisição a cada 5–15 minutos, mas a página não documenta um serviço público de tiles XYZ pronto para uso no mapa.

## Decisões de integração

- Solicitar o manifesto somente quando o piloto ativar a camada; não acrescentar latência à abertura de planos nem consultar fonte externa ao alternar fichas.
- O servidor usa hosts fixos da RainViewer, valida frame e coordenadas e faz proxy autenticado dos tiles. Isso mantém o caminho de rede alinhado com o servidor meteorológico do produto e impede que parâmetros da rota escolham URLs arbitrárias.
- Mostrar a máscara de cobertura junto com os tiles de precipitação e uma legenda que explique que áreas sem cobertura não significam ausência de chuva. Se a máscara falhar, não declarar a camada plenamente interpretável.
- Mostrar a atribuição RainViewer com link enquanto a camada estiver ativa. Exibir o horário do frame quando fornecido.
- Não gravar frames nem metadados no plano; o resultado é temporário e só visual.
- Não usar o RainViewer para cálculos, alertas, condições de voo ou validação de rota.

## Referências

- [RainViewer API](https://www.rainviewer.com/api.html)
- [RainViewer Weather Maps API](https://www.rainviewer.com/api/weather-maps-api.html)
- [RainViewer Brazil: cobertura e fontes listadas](https://www.rainviewer.com/radars/brazil.html)
- [Governo Federal: dados de satélite e radar do INPE](https://www.gov.br/pt-br/servicos/acessar-gratuitamente-dados-e-produtos-derivados-de-satelites-radares-e-instrumentos-meteorologicos-correlatos)
- [CPTEC/INPE SOS Chuva](https://satelite.cptec.inpe.br/soschuvaapp/)
- [INPE: produtos CAPPI da Rede Brasileira de Radares](https://data.inpe.br/dados/radares-meteorologicos/)
