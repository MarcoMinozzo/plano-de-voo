# Data Model: Enxugar a tela do piloto

Nenhuma entidade nova. Nenhum campo novo.

A tela lê o que o plano já guarda. Os dados deste voo passam a ser `numero_passageiros`, `peso_pessoas_kg` e `peso_bagagem_kg`. O combustível não é campo do plano: o cálculo lê `combustivel_valor` e `combustivel_unidade` da aeronave.

O filtro de origem e destino não acrescenta campo. Usa o identificador e o nome que a opção já mostra. A cidade não é atributo desta tela.

Um plano antigo pode ainda ter `ocupantes`, `peso_piloto_kg`, `peso_passageiro_kg` e `combustivel_a_bordo_gal`. Na alteração, a tela soma os dois pesos de pessoas e usa `ocupantes` como número de passageiros. O combustível antigo não volta ao formulário. Não há coluna nova.
