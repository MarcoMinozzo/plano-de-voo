---
name: Plano de voo
status: final
sources:
  - specs/004-enxugar-tela-piloto/spec.md
updated: 2026-11-24
---

# Plano de voo — Experiência

`DESIGN.md` é a identidade visual. Este documento é o comportamento. Os dois vencem qualquer mock se houver conflito. Imagens: `imports/blueprint-airport-runway.jpg`, `imports/emblema-plano-de-voo.png`. Telas de referência: `mockups/key-entrar.html` (Entrar), `mockups/key-processando.html` (Processando), `mockups/key-plano.html` (Plano). Cadastro repete o vidro de Entrar. Voos planejados e o PDF ficam só nestas tabelas.

## Foundation

Web responsiva, um produto só. Telefone e computador usam as mesmas telas, com coluna própria abaixo de 720 px. Não há biblioteca de componentes. O servidor continua dono do cálculo, da meteorologia, da carta, do radar e do PDF. A tela coleta, espera e mostra o retorno.

Os campos do plano novo continuam os de `specs/004-enxugar-tela-piloto/spec.md`: tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem.

## Information Architecture

| Superfície | Chega por | Função |
|---|---|---|
| Entrar | Abrir o produto | Identificação e senha |
| Cadastro | Entrar | Criar a identificação, no mesmo vidro |
| Plano novo | Entrar com sucesso, ou Novo voo | Dados deste voo |
| Processando | Enviar o plano novo ou a alteração | Espera até o servidor responder |
| Plano | Cálculo aceito, ou um voo da lista | Resumo, fichas dos trechos, mapa |
| Voos planejados | Menu | Lista dos planos deste piloto |
| PDF | Imprimir voo | Relatório do plano aberto, com o checklist sugerido |

O menu Novo voo, Voos planejados, Imprimir voo e Sair existe depois da entrada. Entrar e Cadastro não mostram esse menu.

## Voice and Tone

Português de planejamento. Frases curtas. A unidade e a fonte aparecem com o número. Falta de dado diz "indisponível".

| Faça | Não faça |
|---|---|
| "Em processamento" | "Calculando a magia do seu voo" |
| "Não é autorização de voo." | "Pronto para decolar" |
| "METAR da saída" e o nome da medida | Um parágrafo inventado a partir do boletim |
| "Lista local. Não é o catálogo do país." | Completar aeródromo que a caixa não tem |
| A mesma frase quando a identificação falha | Dizer se faltou a pessoa ou a senha |

## Component Patterns

| Componente | Onde | Regra |
|---|---|---|
| page-background | Todas as superfícies | A planta da pista permanece. A troca de tela não troca o fundo. |
| emblem | Entrar, Cadastro, menu | É o emblema importado. Não há outro logo. |
| glass-card | Entrar, Cadastro, Plano novo, resumo | Um card central. No plano calculado, o resumo permanece acima das fichas. |
| text-field | Entrar, Cadastro, Plano novo | Rótulo visível. O valor recusado continua no campo. |
| select-field | Plano novo | Caixa de uma linha. Com mais de doze aeródromos, o texto filtra pelo código ou pelo nome já mostrado. |
| primary-button | Entrar, Cadastro, Plano novo | Uma ação: entrar, criar ou calcular. |
| menu-bar | Plano novo, Processando, Plano, Voos planejados | Novo voo abre o card vazio. Voos planejados abre a lista deste piloto. Imprimir voo pede o PDF do plano aberto. Sair encerra a sessão. |
| processing | Processando | O card some. A ampulheta gira com "Em processamento" até a resposta. |
| summary-card | Plano | Resume cada trecho com os códigos e os números já gravados. Não muda ao trocar a aba. |
| leg-tab | Plano | A aba mostra o código de saída e o de chegada. O clique traz essa ficha para a frente. |
| leg-ficha | Plano | Ordem: grandezas do trecho, METAR da saída, METAR da chegada, mapa, sequência calculada. |
| measure-field | Plano | Unidade no título da grandeza. Fonte uma vez na ficha. Valor diferente traz a própria unidade e a própria fonte. |
| map-panel | Plano, quando há ao menos dois pontos | Carta de voo visual ou mapa de ruas. Radar de chuva liga ou desliga sobre a escolha. Zoom visível. No mapa de ruas, a frase de que ele não substitui a carta fica ao lado. |
| sequence-line | Plano | Depois do mapa, ou no fim da ficha quando não há mapa: saída, chegada e números já gravados. Sem técnica de pilotagem. |
| disclaimer | Entrar, Plano novo, Plano, PDF | A frase de que o resultado apoia o planejamento e não autoriza o voo fica visível sem um clique. |
| pdf-report | PDF | Diagrama técnico do voo inteiro. Checklist sugerido só aqui, com texto e fonte, sem "marcado" e sem "não marcado". |

## State Patterns

| Estado | Superfície | Tratamento |
|---|---|---|
| Primeira abertura | Entrar | Card de vidro, emblema, identificação e senha. |
| Recusa de entrada | Entrar | A mesma frase para identificação inexistente e senha errada. Os campos continuam. |
| Bloqueio | Entrar | Depois de cinco recusas em 15 minutos, a mesma frase, por 15 minutos. |
| Senha curta | Cadastro | A criação não segue. O card permanece, com os valores. |
| Lista local | Plano novo | Uma frase diz que a lista não é o catálogo do país. |
| Sem aeronave | Plano novo | A caixa fica vazia e a frase de que não há aeronave fica visível. |
| Recusa da conta | Plano novo | A ampulheta sai. O card volta com os valores e o motivo, inclusive a opção das caixas. |
| Hora no passado | Plano novo | A confirmação só aparece quando a hora já passou. |
| Espera | Processando | Só a ampulheta e "Em processamento". |
| Plano aceito | Plano | Resumo fixo e a primeira ficha na frente. |
| Vários trechos | Plano | Uma aba por trecho. A aba escolhida fica na frente. |
| METAR presente | Plano | Um bloco da saída e um da chegada. Cada medida do texto tem campo nomeado. |
| METAR ausente | Plano | O bloco daquele aeródromo diz indisponível. Medida que o texto não traz diz indisponível. |
| Carta ausente | Plano | A escolha Carta de voo visual diz indisponível. Nenhum outro desenho ocupa o lugar da carta. |
| Sem dois pontos | Plano | O mapa não aparece. A sequência calculada continua na ficha. |
| Lista vazia | Voos planejados | A frase diz que não há voo planejado. Novo voo continua no menu. |
| Sem plano aberto | Menu | Imprimir voo permanece visível e responde "Não há voo para imprimir." |
| Plano de outro piloto | Plano, PDF, lista | A tela não mostra o voo. A ação é recusada. |
| Sessão vencida | Qualquer tela autenticada | Volta para Entrar. Oito horas sem uso ou Sair encerram a sessão. |

## Interaction Primitives

Toque e ponteiro. Não há atalho de teclado próprio.

- O botão principal envia o card.
- A aba troca a ficha da frente. As outras permanecem atrás, com o resumo quieto acima.
- Carta de voo visual, Mapa de ruas e Radar de chuva são botões visíveis, não um gesto escondido.
- O zoom do mapa tem controle visível.
- Sair é uma ação do menu, não um gesto de voltar do navegador.
- Em tela estreita, as abas rolam na horizontal. O miolo da ficha rola na vertical.

## Accessibility Floor

- O rótulo de cada campo fica visível, ligado ao controle.
- A ampulheta tem texto "Em processamento", não só o desenho.
- A aba da frente se anuncia como selecionada.
- O foco do teclado do navegador permanece visível sobre `{colors.gold}` no vidro e sobre `{colors.navy}` no papel.
- Texto de grandeza, fonte e indisponível entra na ordem de leitura da ficha.
- Cor não é o único sinal da aba da frente: a aba selecionada também muda o texto para o estado selecionado.
- O aviso de que o resultado não autoriza o voo não depende de cor.

## Responsive & Platform

| Largura | Comportamento |
|---|---|
| Abaixo de 720 px | Uma coluna. Menu em botões que quebram a linha. Card na largura útil. Abas em faixa horizontal. Mapa na largura da ficha. |
| De 720 px para cima | Card de entrada e de plano novo centrados, até 40 rem. Fichas numa coluna de leitura até 48 rem. Abas na mesma faixa, sem espremer o miolo. |

Não é aplicativo nativo. O telefone usa o navegador.

## Key Flows

### Fluxo 1 — Helena calcula o voo

Helena é a piloto desta sessão. O nome dela na especificação é o piloto.

1. Helena abre o produto e vê o card de vidro sobre a planta, com o emblema.
2. Ela entra. O menu aparece e o card pede os sete dados do plano novo.
3. Ela calcula. O card some. A ampulheta gira com "Em processamento".
4. O servidor aceita. O clímax é a ficha da frente: grandezas, METAR da saída e da chegada, mapa e a sequência calculada, com o resumo do voo inteiro parado acima.
5. Ela toca a aba do trecho seguinte e essa ficha vem para a frente.

Falha: a conta recusa. A ampulheta sai, o card volta com os valores e o motivo. A frase de que o resultado não autoriza o voo continua visível no sucesso e na recusa.

### Fluxo 2 — Helena abre um voo e imprime

1. Helena escolhe Voos planejados e vê só os planos dela: origem, destino, partida e estado.
2. Ela abre um plano. As fichas voltam, com a carta de voo visual já gravada ou com indisponível.
3. Ela escolhe o mapa de ruas e liga o radar. A frase de que o mapa não substitui a carta fica ao lado.
4. O clímax da impressão: Imprimir voo entrega o PDF com o voo inteiro, unidade, fonte e o checklist sugerido. A tela não mostrou o checklist.

Falha: ela pede Imprimir voo sem um plano aberto. O menu responde "Não há voo para imprimir." e permanece na superfície atual.

### Fluxo 3 — Helena não entra

1. Helena erra a senha. A frase é a mesma de uma identificação que não existe.
2. Na quinta recusa dentro de 15 minutos, a entrada fica fechada por 15 minutos, com a mesma frase.
3. O clímax é a porta quieta: o card não explica qual dos dois dados falhou.

Falha de cadastro: senha com menos de 8 caracteres não cria a identificação. O mesmo card permanece.
