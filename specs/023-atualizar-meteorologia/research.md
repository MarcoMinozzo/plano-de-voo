# Research: Atualizar meteorologia ao consultar o plano

## Decisões

### Atualizar dados ao abrir um plano salvo

- **Decisão**: A consulta GET do detalhe monta os dados meteorológicos atuais para a resposta, sem gravá-los na base.
- **Evidência**: `servidor/planos.py` chama `tempo.buscar` ao montar o plano e grava `meteorologia` e `radar`. `app.py` em `ver_plano` apenas lê o plano e passa esses snapshots para a tela ou JSON.
- **Racional**: Reabre planos antigos com dados atuais sem tornar GET uma operação de escrita ou recalcular a rota. O PDF e os snapshots persistidos ficam fora deste escopo.
- **Alternativas consideradas**: Persistir em cada GET adicionaria efeitos colaterais e poderia sobrescrever o último snapshot válido com falha temporária; recalcular o plano alteraria comportamento alheio ao pedido.

### Consultar apenas METAR/TAF e radar

- **Decisão**: Reutilizar `meteorologia` por aeródromo e `radar` uma vez para a rota.
- **Racional**: `tempo.buscar` também consulta vento de área e carta. Reutilizá-lo inteiro na abertura faria chamadas externas que não fazem parte deste ajuste.
- **Alternativas consideradas**: Chamar `buscar` e descartar vento/carta criaria tráfego desnecessário.

### Tratar ausência como indisponibilidade

- **Decisão**: Não completar boletins ausentes por estação próxima nem usar snapshots anteriores como se fossem atuais.
- **Evidência**: A consulta real ao Aviation Weather Center retornou HTTP 204 para SBJD e um METAR para SBGR.
- **Racional**: A ausência legítima de observação não é uma falha que possa ser corrigida pelo aplicativo; preencher dados violaria a constituição.

### Radar exige configuração externa

- **Decisão**: Manter radar indisponível sem `REDEMET_API_KEY`; não adicionar nem registrar credencial.
- **Evidência**: O carregador local não encontra valor configurado; `radar` já retorna estado indisponível e motivo antes de fazer requisição.
- **Racional**: Não há como obter dados reais da REDEMET sem credencial válida. A lógica da fonte pode ser validada com respostas simuladas até que a chave seja configurada.

## Sem novas escolhas de tecnologia

O projeto já usa `requests`, Flask, SQLAlchemy e pytest. Não há dependência, endpoint ou migração novos.
