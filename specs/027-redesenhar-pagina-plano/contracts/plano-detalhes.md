# UI Contract: Detalhes do plano

## Resumo e fichas

- Um card principal agrupa resumo, rota, abas e conteúdo dos trechos.
- Em telas largas, o card ocupa aproximadamente 80% da viewport; em telas estreitas, ocupa a largura útil sem overflow horizontal.
- A primeira seção apresenta a sequência completa de origem, escalas e destino.
- As fichas mostram nomes completos de origem/destino. Títulos e abas continuam usando ICAO.
- Os cards de origem e destino apresentam os campos ROTAER disponíveis e os contatos publicados; ausência é identificada como indisponível.
- Alertas de excesso de peso ou limite aparecem em vermelho e como texto; o conteúdo vem do resultado do servidor.

## Mapa e fontes

- Controles liga/desliga ficam dentro da parte superior do mapa, com foco e estado acessíveis.
- Mapa de ruas é a base inicial e permanece identificado como mapa de ruas.
- Google Maps aparece desativado enquanto não houver chave local.
- REDEMET é o radar oficial. RainViewer é uma sobreposição suplementar, independente, desligada inicialmente e identificada como não oficial.
- A camada de cobertura RainViewer não é desenhada sobre o mapa. Ao ativar RainViewer, a interface mantém crédito com link, horário da fonte e aviso curto de cobertura não garantida.
- WAC fica identificada como indisponível até validação; OpenAIP sem configuração não gera controle nem mensagem extensa.
- Radar desligado é comunicado pelo botão desativado/estado não selecionado, sem mensagem separada redundante.
- Falha de imagem/tile ou limites inválidos remove a sobreposição e mostra indisponibilidade; não troca de fonte silenciosamente.
## Conteúdo removido

- Remover a seção “Como ler este plano” e o link de PDF no rodapé.
- Manter o botão de impressão no topo e o aviso geral didático/de não autorização de voo.
