# Pesquisa: Priorizar TAF da REDEMET

## API oficial REDEMET

- **Decisão**: Consultar o produto oficial de mensagens TAF da REDEMET pelo indicativo ICAO do aeródromo.
- **Evidência documental**: A página de ajuda do DECEA descreve `https://api-redemet.decea.mil.br/mensagens/taf/{localidades}`, resposta JSON autenticada e parâmetros `data_ini` e `data_fim` no formato `YYYYMMDDHH`, além de `fim_linha`.
- **Referência**: [API-REDEMET: Mensagem TAF — Central de Ajuda DECEA](https://ajuda.decea.mil.br/artigos/api-redemet-mensagem-taf)
- **Evidência ao vivo**: Consulta autenticada a `SBMT` no período de 2026-11-27 00Z a 10Z retornou HTTP 200 e duas mensagens. Os registros continham `id_localidade`, `mens`, `recebimento`, `validade_inicial` e `validade_final`; a mensagem mais recente era de 04:20Z e válida de 06Z a 18Z. A chave não foi incluída na saída nem no repositório.

## Seleção e fallback

- **Decisão**: REDEMET é a fonte prioritária de TAF; AWC permanece como fallback quando REDEMET não fornece uma mensagem utilizável.
- **Racional**: A fonte oficial REDEMET tem cobertura demonstrada para SBMT, enquanto o produto atual consulta AWC exclusivamente. Preservar AWC evita reduzir a disponibilidade em outros indicativos.
- **Validação**: Aceitar apenas resposta bem-sucedida, mensagem não vazia, mesmo indicativo consultado e horários interpretáveis; escolher a maior data de recebimento entre mensagens elegíveis. Resposta vazia, inválida, erro de rede ou chave ausente aciona AWC.
- **Alternativa rejeitada**: Fazer fallback para TAF de estação próxima; o TAF é específico do aeródromo e não pode ser atribuído a outro indicativo.

## Integração existente

- `servidor/tempo.py::meteorologia` consulta AWC METAR e TAF de forma independente.
- `servidor/tempo.py::meteorologia_rota` consulta cada aeródromo distinto e só usa estação regional para METAR.
- `app.py::ver_plano` atualiza a meteorologia ao abrir um plano, sem persistir o resultado.
- `servidor/planos_consulta.py::construir_fontes_relatorio` já aceita proveniência por observação, mas hoje usa a fonte de nível de boletim como fallback. O TAF REDEMET deve fornecer sua própria fonte.
- A mensagem bruta TAF já é exibida em português na ficha e no PDF; a tabela de fontes identifica fonte e horário.

## Falhas e dados antigos

- Falhas de REDEMET devem ser registradas com indicativo e produto, sem URL completa ou credenciais.
- O fallback AWC ocorre apenas para a mesma localidade.
- Nenhum resultado atual do endpoint é gravado durante GET; os planos antigos permanecem com snapshots anteriores, enquanto a página mostra a consulta atual.
