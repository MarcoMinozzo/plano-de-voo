# Modelo de dados: Corrigir carga do ROTAER

O PostgreSQL continua sendo a fonte do catálogo usado pela aplicação. Nenhum dado de aeródromo é inferido da lista local.

## Aerodromo publicado

| Campo | Regra |
| --- | --- |
| `icao` | Identificador publicado; chave existente |
| `nome`, `tipo` | Dados da publicação atual; somente tipo `aerodromo` entra no catálogo nacional |
| `lat`, `lon`, `elev_m` | Coordenadas e elevação da resposta detalhada oficial; obrigatórias para registro carregado |
| `rotaer_versao_id` | Versão individual AISWEB (`<id>`); opcional somente para dados legados/semente |
| `rotaer_atualizado_em` | Data AISWEB (`<dt>`); opcional somente para dados legados/semente |
| `emenda_id` | Emenda corrente já persistida |
| `fonte` | Identifica AISWEB ROTAER vigente e a versão/data individual do registro |

O cache de detalhes é válido somente quando o ICAO, `rotaer_versao_id` e `rotaer_atualizado_em` da lista coincidirem com o registro salvo e os campos de posição e elevação estiverem completos. Um novo identificador de versão invalida o cache.

## Carga da publicação

1. Ler todas as páginas da lista vigente e validar o total anunciado.
2. Descartar tipos diferentes de aeródromo de avião.
3. Reutilizar detalhes validados para versões sem alteração; consultar individualmente os demais.
4. Conferir que cada detalhe corresponde ao ICAO solicitado e contém latitude, longitude e elevação.
5. Só depois de todos os registros completos, marcar a nova emenda disponível e persistir o catálogo.

Uma falha antes da etapa final não grava um catálogo parcial como vigente. Em registros legados, a ausência dos campos de cache força uma consulta detalhada.
