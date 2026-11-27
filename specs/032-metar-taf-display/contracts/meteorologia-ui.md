# Contrato interno: leitura meteorológica na página

## METAR

A ficha do aeródromo apresenta:

1. Identificação do boletim, fonte e horário que já existirem.
2. Tabela de campos interpretados em português com unidade.
3. Fenômenos como código original e explicação conhecida; códigos parcialmente ou não interpretados ficam marcados.
4. String original completa em bloco monoespaçado de fundo quase preto e texto claro.

## TAF

A ficha apresenta:

1. String original completa em bloco monoespaçado de fundo quase preto e texto claro.
2. Tabela de grupos ordenada conforme a mensagem: período base, FM, BECMG, TEMPO e PROB quando existirem.
3. Período/janela e campos de vento, visibilidade, fenômenos e nuvens associados somente ao respectivo grupo.
4. Tokens não interpretados ficam visíveis; nenhum campo é preenchido por inferência.

## Apresentação responsiva

- Cabeçalhos e rótulos são em português.
- Tabela pode rolar dentro de seu contêiner estreito; o documento não ganha rolagem horizontal.
- String original usa monoespaço, preserva espaços e quebra linhas longas no contêiner.
- A indisponibilidade existente substitui leitura vazia ou fabricada.
