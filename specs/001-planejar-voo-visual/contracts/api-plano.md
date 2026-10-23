# Contrato HTTP: plano de voo visual

O contrato da rota com escalas está em `specs/002-rota-com-escalas/contracts/api-rota.md`. Este contrato é o do plano direto.

Páginas e respostas em português. Sessão do Flask identifica o piloto. Rota de plano que não pertence à sessão responde recusa e não revela se o plano existe. Corpo de erro diz o campo ou a fonte que falhou. Não inventa tempo, vento, carta nem radar.

Grandezas saem com valor, unidade e fonte.

## Sessão

### `POST /cadastro`

Cria identificação e senha e abre a sessão.

- Entrada: identificacao, senha com no mínimo 8 caracteres.
- Sucesso: painel vazio.
- Erro: identificação já usada, ou senha com menos de 8 caracteres. A recusa de senha curta diz a regra.

### `POST /entrar`

- Entrada: identificacao, senha.
- Sucesso: painel com os planos desse piloto.
- Erro: a mesma mensagem quando a identificação não existe, a senha está errada ou a identificação teve cinco recusas nos últimos 15 minutos. Nesse último caso a recusa dura mais 15 minutos, mesmo com a senha certa. Nenhum plano é mostrado.

A sessão dura até sair ou até 8 horas sem uso. O cookie é HttpOnly e SameSite=Lax, e Secure quando o acesso não é local. `POST /sair` invalida a sessão. Reutilizar a sessão antiga não abre planos.

A orientação exibida na tela e no PDF é o texto de `documentacao/piloto.md`.

## Catálogos

### `GET /aeronaves`

Lista aeronaves com manual. Exige sessão. A primeira é o Cessna 140, com os limites e a fonte do manual. Não inclui senha nem dados de outro piloto.

### `GET /aerodromos`

Lista indicativos conhecidos, nome, coordenada, elevação e fonte. Exige sessão.

## Planos

### `POST /planos`

Cria e calcula.

- Entrada: aeronave, origem, destino, hora de partida, dados particulares (ocupantes, pesos, combustível a bordo), e confirmação se a hora estiver no passado.
- Sucesso: plano `calculado` ou `inaceitavel`, com resultado, checklist sugerido, aviso educacional, e cada fonte externa preenchida ou `indisponivel`.
- Erro: origem igual ao destino, indicativo desconhecido, manual incompleto, dado particular vazio. Nada é gravado.

### `GET /planos`

Lista só os planos do piloto da sessão: origem, destino, hora, aeronave e estado.

### `GET /planos/{id}`

Devolve o plano completo do piloto da sessão, inclusive checklist, tempo, vento, carta, radar e aviso.

### `PUT /planos/{id}`

Edita origem, destino, hora ou dado particular. Recalcula. Busca de novo tempo, vento, carta e radar. Atualiza o checklist sugerido. Exige sessão e dono.

### `DELETE /planos/{id}`

Apaga depois de confirmação explícita no corpo (`confirmar: true`). Sem essa confirmação, o plano permanece. Exige sessão e dono.

### `POST /planos/{id}/checklist/{item}`

Marca ou desmarca um item do plano do piloto da sessão.

### `GET /planos/{id}/pdf`

Devolve o PDF do plano do piloto da sessão. O arquivo contém rota, horários, combustível, vento, resumo do tempo, checklist e o aviso de que o documento não autoriza o voo. Item externo indisponível aparece como indisponível no PDF.

## Fontes externas, do lado do servidor

O navegador não chama essas fontes.

| Dado | Fonte | Se falhar |
| --- | --- | --- |
| METAR e TAF | Aviation Weather Center, tempo limite 8 s | `indisponivel` |
| Radar | REDEMET MaxCappi, chave no ambiente | `indisponivel` |
| Carta | AISWEB WAC vigente, chave no ambiente | `indisponivel` |
| Vento de rota | Produto de área da REDEMET | `indisponivel` |
