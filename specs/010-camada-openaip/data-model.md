# Modelo de dados — Camada aeronáutica OpenAIP

## Entidades conceituais

### Estado da camada

- `disponivel`: há chave configurada e o serviço entrega tiles válidos.
- `indisponivel`: chave ausente, autorização negada, limite de uso, falha de
  rede ou resposta inválida.
- Seleção: ruas inicialmente; OpenAIP somente após ação explícita do piloto.

### Tile solicitado

- Plano associado: identifica o plano cuja sessão autenticada pode consultar.
- Coordenadas: zoom, coluna e linha TMS, validadas antes da requisição.
- Conteúdo: resposta PNG do provedor; não é persistida pela aplicação.

## Persistência

Nenhuma entidade nova no PostgreSQL. O estado da camada é resolvido por
requisição e pela configuração do serviço. A chave fica em variável de
ambiente e não é persistida em plano, HTML, log ou resposta ao cliente.

## Relações e invariantes

- O tile só pode ser obtido pela sessão do piloto dono do plano.
- A seleção OpenAIP não altera rota, cálculo, estado do radar ou disponibilidade
  da carta AISWEB.
- A atribuição é exibida enquanto a camada estiver ativa.
