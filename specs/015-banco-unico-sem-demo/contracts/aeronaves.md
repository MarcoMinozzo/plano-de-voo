# Contrato: Catálogo de aeronaves

## Seleção na aplicação

- O catálogo factual continua sujeito à disponibilidade do RAB, à completude
  das fontes e ao limite existente de trinta modelos.
- A categoria didática expõe os vinte proxies, separada do catálogo factual,
  mesmo quando o RAB não estiver disponível.
- Nenhum dos vinte perfis genéricos “Aeronave DEMO 01–20” é exposto.
- Cada proxy é identificado como “perfil sintético didático — valores não
  validados; não representam dados do modelo associado”.
- A indisponibilidade de ROTAER continua impedindo o cálculo de rota; proxies
  não substituem dados oficiais de aeródromos.

## Plano e PDF

Ao usar um proxy, resultado e PDF repetem o rótulo sintético e o aviso de que
o conteúdo não serve para planejamento de voo real, não substitui manual,
treinamento ou norma e não autoriza voo.

## API JSON

`GET /aeronaves` mantém o estado do catálogo factual e apresenta a lista
didática em campo separado. A resposta não contém `modo_demo` nem depende de
um estado de ambiente DEMO. Cada proxy inclui sua identidade de exercício e
indicador de dado sintético.
