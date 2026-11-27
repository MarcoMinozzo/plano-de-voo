# Pesquisa — Mapa quadrado com satélite REDEMET e WAC visível

## Decisões

- **Satélite**: consultar o produto oficial REDEMET `realcada` sob demanda, usando a chave `REDEMET_API_KEY` já configurada no servidor. Selecionar o frame mais recente com URL, data/hora e caixa geográfica válidas.
- **Sobreposição**: desenhar a imagem nos limites informados pela API, abaixo da rota e independente do pane do radar. Exibir fonte REDEMET e o horário exatamente como retornado.
- **Falha**: ausência de chave, erro remoto, frame vazio ou metadados inválidos resultam em indisponibilidade; não usar imagem antiga, mapa alternativo ou limites estimados.
- **WAC**: manter documentos AISWEB e diálogo atual. A opção fica sempre visível e desabilitada quando não há documento validado. Não produzir raster ou tiles nesta feature.
- **Layout**: quadro quadrado em desktop; manter dimensões e controles móveis atuais. Reutilizar classes e CSS do projeto, sem dependências.

## Evidências e fontes

- O endpoint oficial `https://api-redemet.decea.mil.br/produtos/satelite/realcada` fornece resposta com `data.lat_lon` (`lat_min`, `lat_max`, `lon_min`, `lon_max`) e lista de imagens `data.satelite`, incluindo `data` e `path`. O exemplo indexado pelo domínio oficial também mostra imagens PNG hospedadas em `estatico-redemet.decea.mil.br`.
- O portal oficial de cadastro da API é `https://api-redemet.decea.mil.br/cadastro-api/`. A aplicação já mantém a chave REDEMET em configuração de servidor e usa `_get` com timeout em `servidor/tempo.py`.
- O serviço atual `tempo.radar` demonstra o padrão de integração REDEMET; `app.py:camada_radar` demonstra autenticação, autorização do dono e resposta JSON sem persistência.
- `servidor/tempo.py:carta` e a spec 009 confirmam que AISWEB entrega PDFs, não tiles prontos. A autorização e a validade de derivados WAC permanecem sem comprovação; a UI não deve fingir que o PDF é camada georreferenciada.

## Alternativas consideradas

- **Renderizar a imagem como camada base**: rejeitado; a imagem de satélite é um overlay e o mapa de ruas permanece como base inicial.
- **Reutilizar radar ou RainViewer como imagem satélite**: rejeitado; são produtos diferentes.
- **Servir tiles WAC derivados do PDF**: rejeitado nesta mudança porque edição, cobertura, georreferenciamento e autorização ainda são gates pendentes na feature 009.

## Limitações

- A disponibilidade e o frame mais recente dependem do serviço externo e da chave do ambiente. Testes automatizados devem usar respostas simuladas; nenhum teste depende de disponibilidade ao vivo.
- A URL de imagem só é aceita no host REDEMET observado. Mudança de host deve falhar fechada até validação e atualização do contrato.
