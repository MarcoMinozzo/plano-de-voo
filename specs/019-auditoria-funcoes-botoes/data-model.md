# Modelo de dados: Auditoria de funções, botões e camadas

Não há alteração de esquema, banco ou registro de negócio.

## Dados reutilizados

### Perfil do piloto

- Campo existente: `Piloto.nome_exibicao`.
- A rota valida e persiste o nome do piloto autenticado.
- A mensagem de sucesso é transitória na resposta seguinte ao POST; não é gravada no banco.
- Erros de validação não produzem estado de sucesso.

### Disponibilidade do radar

- Estrutura existente: JSON com `estado`, URL, limites geográficos, horário e fonte quando disponível.
- Campo opcional adicionado: `motivo`, texto categorizado quando `estado` é `indisponivel`.
- Motivos devem distinguir chave REDEMET ausente, ausência de dados/limites válidos e fonte indisponível.
- Planos antigos sem `motivo` permanecem válidos e exibem fallback genérico verdadeiro.

### Fontes aeronáuticas

- A disponibilidade de WAC/OpenAIP não ganha novos campos nem migrações nesta mudança.
- A tabela de procedência mantém todas as colunas; apenas a área de rolagem visual muda.
