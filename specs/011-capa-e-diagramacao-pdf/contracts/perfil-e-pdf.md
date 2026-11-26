# Contrato — Perfil e relatório PDF

## Perfil

- `GET /perfil`: exige sessão e mostra somente o nome do piloto autenticado.
- `POST /perfil`: atualiza somente o nome do piloto autenticado.
- O cadastro solicita identificação, senha e nome de exibição.
- Nome é aparado; vazio ou acima de 160 caracteres é recusado com mensagem
  clara, sem alterar dados.
- A sessão não pode fornecer `piloto_id` de destino para a atualização.
- O menu autenticado oferece acesso ao perfil.

## PDF

- `GET /planos/{plano_id}/pdf`: mantém sessão obrigatória e filtro de
  propriedade atual; plano alheio retorna `404`.
- `200 application/pdf`: capa própria com emblema, nome do produto, nome atual
  do piloto, rota ordenada completa e data/hora de partida; demais páginas
  organizam o conteúdo completo do plano.
- O fuso exibido deve refletir o valor armazenado na data/hora de partida.
- Não expor identificação de acesso no lugar do nome de exibição depois que o
  perfil estiver migrado.
- A resposta não persiste arquivo nem altera dados do plano.

## Conteúdo preservado

Manter unidades, fontes, procedência, estados indisponíveis, avisos educacionais,
dados DEMO/sintéticos, checklist sugerido sem estado marcado e documentação
integral do piloto.
