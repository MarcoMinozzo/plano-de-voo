# Modelo de dados: Banco único e perfis sintéticos didáticos

## Perfil proxy sintético

Representa um dos vinte perfis associados a um modelo como tema de exercício,
sem afirmar que os valores correspondam ao modelo real.

| Atributo | Regra |
|---|---|
| Identidade | Fabricante/modelo-alvo do perfil proxy |
| Categoria | Perfil sintético didático, separado do catálogo factual |
| Valores técnicos | Os seis valores atuais devem ser copiados sem alteração |
| Unidades | Preservadas por campo |
| Proveniência | Identificação de dado sintético; referências genéricas não provam aplicabilidade ao alvo |
| Extrato RAB | Não vinculado ao extrato sintético da base antiga |

Cada perfil tem seis fontes técnicas sintéticas: peso vazio, peso máximo de
decolagem, limite de bagagem, combustível utilizável, velocidade de cruzeiro
e consumo de cruzeiro. Velocidade e consumo mantêm o perfil associado atual.

## Base de origem da migração

É consultada somente para leitura. A migração seleciona exatamente os vinte
registros `proxy_sintetico` e suas fontes. Perfis genéricos, extrato RAB
sintético, pilotos, planos e demais entidades não são transferidos.

## Base canônica do produto

Preserva seus registros atuais de ROTAER, RAB, pilotos e planos. Recebe os
vinte proxies com novos IDs e fontes relacionadas pelos novos IDs de aeronave.
`extrato_id` dos proxies fica nulo para separá-los dos modelos factuais.

## Regras de estado da migração

1. Validar que a origem contém os vinte perfis esperados antes de escrever.
2. Perfis já existentes com identidade, valores e unidades iguais são
   considerados importados e não são alterados.
3. Qualquer perfil conflitante ou ausente interrompe a operação sem mudanças
   parciais no destino.
4. A origem nunca recebe escrita; a transação cobre todas as inserções no
   destino.
