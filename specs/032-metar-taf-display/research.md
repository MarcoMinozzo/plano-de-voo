# Pesquisa: Apresentação legível de METAR e TAF

## Padrões meteorológicos

- **Decisão**: Interpretar grupos METAR/TAF no servidor e manter a string original ao lado da leitura.
- **Racional**: Os boletins usam campos e códigos padronizados; a leitura tabular deve ser verificável contra o texto publicado e não deve depender de chamadas adicionais.
- **Referência primária**: [WMO-No. 782 — Aerodrome reports and forecasts](https://library.wmo.int/viewer/30224?medianame=782_2022_edition_en_), guia de codificação METAR/SPECI/TAF, atualizado em 27/11/2025 conforme a publicação.
- **Referência complementar**: [FAA Order JO 7900.5C — Surface Weather Observing](https://www.faa.gov/documentLibrary/media/Order/JO_7900.5C.pdf), estrutura do METAR e elementos do relatório.
- **Grupos TAF**: Interpretar FM como mudança a partir do horário indicado; BECMG como mudança dentro de uma janela; TEMPO como condições temporárias; PROB como probabilidade associada ao grupo. Não misturar valores de grupos distintos.
- **Alternativa rejeitada**: Traduzir no navegador por JavaScript; contraria o princípio do servidor e duplicaria interpretação na camada de apresentação.

## Estrutura existente

- `servidor/tempo.py::campos_metar` já expõe temperatura, ponto de orvalho, vento, visibilidade, altímetro, fenômenos e nuvens com rótulos/unidades em português.
- `servidor/tempo.py::_metar_de_item` retém os valores estruturados da resposta AWC; a observação também mantém `raw` sem alteração.
- `app.py::_boletins_por_aerodromo` prepara os campos METAR usados em `templates/plano.html`.
- A ficha atual exibe METAR em lista de definições e string dentro de `<code>`; TAF é somente texto bruto.
- `static/css/input.css` usa `@source "../../templates"` e `npm run css:build` atualiza `static/css/tailwind.css`; não é necessária nova dependência.

## Tradutor interno

- **Decisão**: Manter um catálogo interno pequeno, determinístico e testado para intensidade, descritores e fenômenos de uso comum; compor a explicação sem remover os códigos.
- **Racional**: Apresenta vocabulário meteorológico em português sem chamada externa e deixa códigos não cobertos explícitos.
- **Limite**: Não explicar token desconhecido com base em semelhança textual; apresentar código e indicação “não interpretado”.
- **Alternativa rejeitada**: Usar tradução automática ou busca on-line durante a renderização; prejudica previsibilidade, fonte e disponibilidade.
