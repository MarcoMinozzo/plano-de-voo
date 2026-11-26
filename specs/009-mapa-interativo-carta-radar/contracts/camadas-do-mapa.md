# Contrato — Camadas do mapa

## Interação da ficha

- Ao abrir, selecionar **Mapa de ruas** e manter **Radar de chuva** desligado.
- **Carta de voo visual** e **Mapa de ruas** são controles mutuamente exclusivos.
- **Radar de chuva** é um controle independente e só pode ser ativado quando há imagem e limites geográficos válidos.
- Preservar rota, zoom, fonte do boletim, mensagem de indisponibilidade e aviso educacional.
- Controles devem expor seleção/estado a leitor de tela e teclado, além de toque.

## Disponibilidade da carta

- A carta é indisponível enquanto algum gate de validação do GeoPDF oficial estiver pendente ou falhar.
- Não há endpoint WMS aprovado nem fallback automático para outra fonte.
- A implementação de uma eventual camada local só será contratada após registrar: arquivo/edição vigente, georreferenciamento e cobertura da rota, autorização para gerar e servir tiles, ambiente reproduzível, e local/ciclo de vida de armazenamento.
- A carta só poderá ser adicionada ao Leaflet após a validação do arquivo e do primeiro carregamento dos tiles derivados autorizados.

### Resultado visível

- Enquanto indisponível, informar “Carta de voo visual indisponível.” e manter o mapa de ruas como base inicial, sem identificá-lo como carta.
- Após implementação futura, o contrato do endpoint e a origem dos tiles devem ser acrescentados a este documento com autorização e formato confirmados.
- Falha de carregamento remove a camada defeituosa e informa indisponibilidade; não troca automaticamente para outra fonte.

## Radar

O mapa usa o payload já entregue em `plano.radar`. A sobreposição só é construída quando estado, URL e limites `lat_min`, `lat_max`, `lon_min`, `lon_max` são válidos. O estado inicial da opção é desligado.
