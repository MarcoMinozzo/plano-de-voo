# Data Model: Apresentação legível de METAR e TAF

## Projeções transitórias

Nenhum registro de banco é criado ou alterado. O servidor prepara dados de leitura apenas para renderizar a página.

### Leitura METAR

- `raw`: texto original, inalterado.
- `campos`: lista de rótulo, valor, unidade e, quando aplicável, explicação de fenômeno.
- Campos existentes continuam preservando os valores AWC e suas unidades.
- Código meteorológico permanece junto à explicação; desconhecidos são marcados como não interpretados.

### Leitura TAF

- `raw`: texto original, inalterado.
- `grupos`: sequência de períodos com tipo (base, FM, BECMG, TEMPO ou PROB), janela publicada, campos interpretados e tokens não reconhecidos.
- Cada grupo contém apenas condições da previsão daquele grupo; mudanças não são mescladas silenciosamente com o grupo base.
- Vento, visibilidade, fenômenos e nuvens são valores publicados com unidades; grupo ausente ou token não reconhecido não gera valor inferido.

### Fenômeno meteorológico

- `codigo`: código original encontrado no boletim.
- `explicacao`: descrição em português dos componentes reconhecidos; componentes desconhecidos recebem a indicação explícita “Código não interpretado”, sem uma descrição inventada.

## Validações

- A leitura não modifica `raw`, consulta fonte externa, persiste resultados nem altera a disponibilidade do boletim.
- Períodos e mudanças TAF permanecem na ordem do texto publicado.
- Campos desconhecidos não são descartados nem associados a descrições aproximadas.
- Tabelas recebem unidades existentes; códigos de visibilidade/nuvens não são apresentados como medidas convertidas sem conversão definida.
