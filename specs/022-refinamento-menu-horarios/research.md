# Pesquisa: Refinamento do menu e horários

## Decisões

- **Navegação móvel:** usar `<details>` e `<summary>` nativos, com nome acessível e sem JavaScript. Isso reaproveita recursos do navegador e preserva teclado/toque sem adicionar dependências.
- **Alinhamento desktop:** posicionar o logo e o menu no mesmo contêiner alinhado ao centro vertical; centralizar o menu independente do espaço ocupado pelo logo.
- **Largura do menu:** deixar o card acompanhar o conteúdo dos itens e adicionar padding horizontal, substituindo a largura fixa de viewport.
- **Ícones:** usar SVG inline decorativo junto aos rótulos e nome acessível no botão Sair, que permanece apenas com ícone visível.
- **Cores:** atualizar os tokens de texto claro e azul de vidro existentes, mantendo a translucidez e evitando uma paleta paralela.
- **Horário:** formatar apenas a apresentação do horário armazenado como data, hora e minuto seguidos de “TL”; não converter o instante nem tocar nos cálculos.

## Alternativas consideradas

- JavaScript para controlar o menu: rejeitado por ser desnecessário para o comportamento recolhível.
- Largura fixa proporcional à tela: rejeitada porque não acompanha o conjunto de palavras.
- Alterar timezone ou persistência: fora do pedido, com risco de mudar cálculos existentes.
