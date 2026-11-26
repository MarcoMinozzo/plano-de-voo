# Pesquisa: Corrigir carga do ROTAER

## Contrato oficial AISWEB

- **Decisão**: Consumir a área `rotaer` sem filtro `amdt` para obter os registros atualmente em vigor. Filtrar aeródromos pelo tipo publicado `AD`.
- **Evidência**: A documentação AISWEB explica que `amdt=last_amdt` limita a resposta aos aeródromos que entraram em vigor naquela emenda; sem `amdt`, são retornados os aeródromos em vigor. O filtro `rowend` é a quantidade de registros, não o índice final.
- **Alternativa rejeitada**: `amdt=last_amdt` não substitui a lista completa vigente; em uma chamada real de diagnóstico retornou zero registros.
- **Fonte**: [Documentação da API AISWEB](https://documenter.getpostman.com/view/7201070/SzKQyg3H).

- **Decisão**: Interpretar `<aisweb><rotaer total="..."><item>...</item></rotaer></aisweb>`, percorrer todas as páginas e validar o total anunciado.
- **Evidência**: A documentação descreve `<item>` com `id` (versão do registro), `type`, `AeroCode`, `name` e `dt` (data de publicação/atualização). Uma chamada real retornou `total=6166`, páginas de 100 itens e dados de tipo `AD` contendo 4519 registros.
- **Alternativa rejeitada**: Tratar cada `<rotaer>` como um registro ignora os `<item>` e resulta em zero aeródromos.

- **Decisão**: Buscar os dados detalhados por `icaoCode`, incluindo `lat`, `lng` e `altM`. Limitar a quatro solicitações simultâneas, persistir `id` e `dt` por aeródromo e reutilizar os detalhes quando ambos não mudarem.
- **Evidência**: A documentação do endpoint detalhado lista `icaoCode` e informa coordenadas e elevação em metros. A lista em vigor não inclui `altM`. Um teste com dois códigos concatenados não retornou detalhes, e a API documenta a consulta detalhada por código individual.
- **Alternativas rejeitadas**: Inventar elevação ou aceitar registros incompletos viola a constituição; repetir milhares de chamadas em cada sincronização é desnecessário quando a versão publicada não mudou.

## Integridade e operação

- **Decisão**: Montar a coleção completa antes de marcar a emenda disponível; interrupção de página ou detalhe mantém o resultado indisponível e registra um motivo seguro.
- **Rationale**: O plano exige catálogo nacional da publicação vigente e não permite misturar dados parciais ou locais.
- **Decisão**: Exibir progresso periódico e não imprimir exceções HTTP completas, que podem conter a URL com os parâmetros de credencial.
- **Rationale**: A carga pode realizar milhares de consultas iniciais; o operador precisa distinguir progresso de travamento sem expor chaves.

## Sem dependências novas

- `requests` continua responsável por HTTP.
- `concurrent.futures` fornece concorrência limitada na biblioteca padrão.
- PostgreSQL e Alembic existentes armazenam os identificadores de versão e a data de publicação.
