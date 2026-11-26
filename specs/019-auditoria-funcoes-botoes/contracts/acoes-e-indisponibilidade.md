# Contrato de ações e indisponibilidade

## Perfil

| Ação | Resposta |
|---|---|
| POST HTML com nome válido | Persistir no piloto autenticado, emitir confirmação transitória e redirecionar ao perfil. |
| POST HTML com nome inválido | Manter resposta de erro e mensagem atual; não emitir confirmação. |
| POST JSON | Preservar o contrato atual `{ok, nome_exibicao}` ou a mensagem de validação. |

## Camadas do mapa

| Estado | Comportamento |
|---|---|
| Ruas | Base habilitada; rota e trecho ativo continuam visíveis. |
| WAC sem gates aprovados | Desabilitada, com os critérios pendentes visíveis; não usa fallback. |
| OpenAIP sem chave | Desabilitada e identificada como fonte comunitária não oficial, com motivo de chave ausente. |
| Radar indisponível | Desabilitado e acompanhado pelo motivo seguro devolvido pelo servidor; se dados antigos não tiverem motivo, informar apenas indisponibilidade. |
| Radar disponível | Só pode ser habilitado com URL e limites geográficos válidos; começa desligado. |

## Tabela de procedência

Todas as colunas continuam presentes. Em tela estreita, apenas o contêiner da tabela recebe rolagem horizontal; a página e os controles fora dela permanecem na largura da viewport.
