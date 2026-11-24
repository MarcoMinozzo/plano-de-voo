# Contract: casca visual

## Todas as páginas

- O fundo visível usa a planta da pista servida em `static/casca/`.
- O único logo é o emblema servido em `static/casca/`, com texto alternativo "Plano de voo".
- Abaixo de 720 px a página não cria rolagem horizontal.

## Entrada e cadastro

- Um card central, com cantos arredondados, contém o emblema.
- A entrada tem identificação, senha e o caminho "Criar acesso".
- O cadastro usa o mesmo fundo, o mesmo emblema e o mesmo card.
- Nenhuma das duas contém os textos "Novo voo", "Voos planejados" nem "Imprimir voo".
- A recusa de entrada continua uma frase só, igual para identificação inexistente e senha errada.

## Plano novo

- O card central lista, nesta ordem, tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem.
- A página não pede combustível a bordo nem peso de piloto separado.
- A frase "Não é autorização de voo." fica visível sem abrir um bloco.
- O menu contém "Novo voo", "Voos planejados", "Imprimir voo" e "Sair".
- "Sair" envia a ação que encerra a sessão. Não é um link de leitura.
- Sem plano aberto, "Imprimir voo" revela "Não há voo para imprimir." na mesma página.
- Ao enviar, o card deixa de estar visível e a página mostra "Em processamento" até a resposta.

## Plano calculado

- Acima dos trechos, um resumo permanece ao trocar a aba.
- Cada linha do resumo traz o código de saída, o de chegada e números já calculados.
- O resumo não contém instrução de técnica de decolagem nem de pouso.
- Com o plano aberto, "Imprimir voo" aponta para o PDF desse plano.

## Fora deste contrato

- O miolo da ficha, o METAR, a carta, o radar e o checklist seguem `specs/004-enxugar-tela-piloto/spec.md`.
