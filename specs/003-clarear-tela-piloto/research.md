# Research: Clarear a tela do piloto

## Decisão: o estado gravado não muda de nome

**Decision**: `calculado` e `inaceitavel` continuam no plano gravado. A tela traduz para "aceitável para planejamento" e "não aceitável".

**Rationale**: A spec pede o que o piloto lê, não um novo valor persistido. Os testes e o PDF que já conhecem o estado interno continuam válidos. Trocar a palavra gravada obrigaria migração sem mudar a conta.

**Alternatives considered**: Gravar o rótulo em português. Rejeitado porque mistura texto de tela com o estado que a conta já produz.

## Decisão: a busca de aeródromo fica no servidor

**Decision**: O navegador envia o texto digitado, com pelo menos dois caracteres que não sejam só espaço, e o servidor devolve só as correspondências da emenda vigente. O navegador mostra identificador e nome. Não recebe a lista nacional.

**Rationale**: A constituição manda a interface só coletar, chamar o servidor e apresentar. Filtrar milhares de aeródromos no navegador baixaria o catálogo inteiro e esconderia a lista atrás de um controle que ainda a contém.

**Alternatives considered**: Uma lista suspensa com todos os aeródromos. Rejeitado pela spec. Um componente de terceiros. Rejeitado porque não há dependência nova.

## Decisão: hora no passado

**Decision**: O pedido de confirmação não está no formulário de uma hora futura. Quando o valor informado já passou, a tela mostra o pedido junto da hora. A conta no servidor continua exigindo a confirmação; a tela só deixa de oferecê-la cedo demais.

**Rationale**: A regra de negócio da hora já está em `montar`. A spec muda quando o piloto vê o pedido.

**Alternatives considered**: Confirmar toda hora passada sem perguntar. Rejeitado porque a spec `001` já pede a confirmação.

## Decisão: alteração não grava recusa de formulário

**Decision**: A alteração abre o formulário com os valores do plano. Se a conta recusa antes de gravar (hora sem confirmação, lugar inválido, manual ausente, catálogo indisponível), o plano anterior permanece e a tela devolve os valores digitados.

**Rationale**: A spec distingue recusa de formulário de plano calculado como não aceitável. O segundo continua gravado, como na spec `002`.

**Alternatives considered**: Gravar também a recusa de formulário. Rejeitado porque apagaria um plano válido com um envio incompleto.

## Decisão: checklist volta ao item

**Decision**: Marcar continua sendo um envio ao servidor. A tela reapresentada abre no item marcado, com o estado visível.

**Rationale**: A spec aceita reapresentar a tela, desde que o item continue visível. Não exige marcação só no navegador.

**Alternatives considered**: Atualizar o item sem reapresentar a página. Aceitável, mas não necessário, e o envio ao servidor já existe.
