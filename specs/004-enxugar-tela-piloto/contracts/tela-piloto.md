# Contract: tela enxuta

## Plano novo e alteração

- Campos, nesta ordem: tipo de avião (`aeronave_id`), origem, destino, data e hora (`hora_partida`), número de passageiros (`numero_passageiros`, mínimo 1), peso das pessoas (`peso_pessoas_kg`) e peso da bagagem (`peso_bagagem_kg`).
- A página não contém `peso_piloto_kg`, `peso_passageiro_kg`, `ocupantes` nem `combustivel_a_bordo_gal`.
- Caixas `select` de `aeronave_id`, `origem` e `destino`, sem atributo `size`.
- Com opções, a caixa fechada mostra um nome, não um convite vazio.
- Grupos com legenda "Rota" e "Carga".
- Com até doze aeródromos, a página não contém `data-filtra`.
- Com mais de doze, cada caixa de aeródromo tem um campo `data-filtra` apontando para o id da caixa.
- Esse texto mantém a opção quando é parte do código ou parte do nome exibido, ignorando maiúsculas e acentos. Não cria opção. A cidade que não esteja no nome exibido não é critério.
- Lista local: o texto "não é o catálogo do país inteiro".
- Frase visível contendo "Não é autorização de voo."
- O artigo longo de orientação não fica aberto no formulário.

## Plano calculado

- A primeira leitura depois do título contém o rótulo de planejamento já usado no painel.
- A tabela de trechos traz a unidade no título quando ela é comum, e uma legenda com `distancia_fonte`, `proa_fonte`, `tempo_fonte` e `combustivel_fonte` do primeiro trecho.
- Todos indisponíveis: o texto "Tempo, vento, carta de voo visual e radar: indisponível."
- Mapa: elemento `id="mapa"` só com dois pontos ou mais. A frase "não substitui a carta de voo visual" fica antes desse elemento.
- `<details>` com resumo "Como ler este plano" contém o texto de `documentacao/piloto.md`, inclusive "Informe de onde sai", "Item indisponível" e "Não é autorização de voo."

## Checklist

- Item não marcado não contém o texto "não marcado".
- Item marcado contém a palavra "marcado".
- A fonte do item permanece no HTML da linha.
