# Contrato: Consulta de plano e meteorologia

## Escopo

Contrato existente para `GET /planos/<id>` em HTML ou JSON. Não é criado endpoint novo nem alterado o controle de acesso.

## Regras

- O plano só é retornado ao piloto proprietário, conforme a validação já existente.
- Cada resposta do detalhe consulta METAR e TAF atuais para cada aeródromo distinto usado nos trechos e consulta radar para a rota, se REDEMET estiver configurada.
- A resposta JSON mantém o formato de `para_json`; os campos `meteorologia` e `radar` contêm os resultados atuais daquela requisição.
- A resposta HTML mantém o layout e apresenta os mesmos resultados atuais nos blocos de METAR/TAF e no estado/controle de radar.
- Uma fonte indisponível não torna o plano inacessível nem invalida resultados de outras fontes.
- A ausência de observação, chave, cobertura ou imagem é apresentada como indisponível, sem fallback silencioso.
- O GET não persiste os resultados meteorológicos, altera os dados do plano nem recalcula a rota.
- Alternar fichas, base cartográfica ou radar no navegador não faz novas requisições ao serviço meteorológico.

## Respostas de erro

- Plano inexistente ou de outro piloto mantém a recusa atual.
- Falha de fonte mantém HTTP e plano disponíveis; o estado específico da fonte é retornado como indisponível.
