# Data Model: Camada suplementar de radar RainViewer

## Dados existentes utilizados

### Plano de voo e mapa

- **Proprietário**: piloto autenticado que pode consultar o plano e seus tiles.
- **Trechos e coordenadas**: pontos já calculados pelo servidor e usados para centrar o mapa.
- **REDEMET**: estado da camada oficial de radar; permanece inalterado e independente.

## Dados temporários da requisição

### Manifesto RainViewer

- **Estado**: disponível ou indisponível, com motivo legível quando indisponível.
- **Host**: host oficial retornado pelo manifesto, aceito somente quando corresponde ao host de tiles permitido.
- **Frame**: caminho/identificador validado e horário Unix do frame escolhido. O horário de geração do manifesto não substitui o horário do frame.

### Tile de radar

- **Coordenadas**: zoom, x e y dentro dos intervalos XYZ válidos, respeitando o zoom nativo máximo documentado.
- **Conteúdo**: imagem PNG válida obtida apenas do host de tiles autorizado.
- **Fonte**: RainViewer, sempre identificada como agregador não oficial.

### Máscara de cobertura

- **Conteúdo**: tile de cobertura da mesma região e nível de zoom.
- **Interpretação**: áreas sem cobertura não podem ser apresentadas como sem precipitação. A máscara é indicativa e pode estar desatualizada.
- **Falha**: se não for possível distinguir cobertura de ausência de eco, a interface comunica cobertura desconhecida e não descreve a área vazia como seca.

## Persistência e relações

Nenhuma tabela, coluna ou migração é adicionada. Manifesto, frame e cobertura são dados temporários; a camada não altera o plano, a meteorologia persistida, a rota ou os cálculos.
