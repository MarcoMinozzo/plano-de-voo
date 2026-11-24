# Research: Aplicar a casca visual

## Estilo sem pacote novo

- **Decision**: O visual fica no CSS já embutido em `templates/base.html`. Não entra biblioteca de componentes nem arquivo de fonte.
- **Rationale**: A constituição exige justificativa para dependência nova. A casca é cor, planta, card e ampulheta. O processo Flask já entrega o HTML.
- **Alternatives considered**: Uma folha separada em `static/` só para o CSS. Rejeitada porque o estilo da tela já mora em `base.html` e separá-lo não muda o que o piloto vê.

## Imagens da planta e do emblema

- **Decision**: As duas imagens fechadas no desenho passam para `static/casca/`, servidas pelo próprio Flask. O fundo de toda página aponta para a planta. O emblema é a única imagem de logo.
- **Rationale**: A constituição já admite `static/` para apresentar o retorno. Não há serviço externo de imagem.
- **Alternatives considered**: Embutir as imagens no HTML. Rejeitada porque a planta é grande e o emblema se repete no menu.

## Ampulheta durante o envio

- **Decision**: Ao enviar o plano novo ou a alteração, um script da página esconde o card, mostra a ampulheta com "Em processamento" e impede Novo voo, Voos planejados e Imprimir voo de abrirem outra tela até o navegador receber a resposta. O script não calcula voo, não lê meteorologia e não monta o PDF.
- **Rationale**: O envio atual espera a resposta do servidor. Sem esse passo na página, o card permaneceria visível durante a espera, o que a especificação recusa.
- **Alternatives considered**: Uma segunda rota só para a espera. Rejeitada porque a conta continua no envio que já existe.

## Menu e impressão

- **Decision**: O menu autenticado fica em `templates/base.html`. Sair continua sendo o envio que encerra a sessão. Imprimir voo, com um plano aberto, aponta para o PDF que esse plano já tem. Sem plano aberto, Imprimir voo revela na mesma página a frase "Não há voo para imprimir." Não há rota nova.
- **Rationale**: A lista, o plano e o PDF já existem. A casca só os nomeia no menu.
- **Alternatives considered**: Uma rota que devolve a frase. Rejeitada porque a frase é da página em que o piloto já está.

## O que permanece na especificação 004

- **Decision**: Esta feature não reescreve a ficha, o METAR, a carta, o radar nem o checklist. O card de resumo entra acima do bloco de trechos que a 004 especifica.
- **Rationale**: A 005 declara esse limite. Mudar a conta ou o conteúdo da ficha aqui misturaria duas features.
- **Alternatives considered**: Implementar as fichas de novo dentro da casca. Rejeitada porque a regra já está em `specs/004-enxugar-tela-piloto/spec.md`.
