# Data Model: Aplicar a casca visual

Nenhuma entidade nova. Nenhum campo novo. Nenhum plano, piloto ou aeródromo muda de forma.

A casca lê o que a sessão e a página já têm.

- **Tela autenticada**: existe quando a sessão tem piloto. O menu aparece. A entrada e o cadastro não têm esse menu.
- **Plano aberto**: a página de um plano da sessão. Só nesse caso Imprimir voo aponta para o relatório daquele plano. Nas outras páginas autenticadas, a ação revela "Não há voo para imprimir."
- **Espera**: estado da página, não do banco. Começa no envio do plano novo ou da alteração e termina quando a resposta chega. O card fica oculto e a ampulheta fica visível. Nada disso é gravado.
- **Resumo**: linhas derivadas dos trechos já calculados. Não é uma tabela nova. Trocar a aba não grava outra escolha.

A planta e o emblema são arquivos em `static/casca/`. Não são registros.
