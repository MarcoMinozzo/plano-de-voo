# Quickstart: Rota com escalas

Conferência depois da implementação. Não substitui `tasks.md`.

## Pré-requisitos

- O plano direto já sobe, como em `documentacao/operacao.md`
- Chave do AISWEB no ambiente, para a carga real do ROTAER e do pôr do sol
- Extrato público vigente do RAB indicado por `RAB_EXTRATO`, sem copiar o arquivo bruto para o repositório
- Fonte técnica oficial ou secundária rastreável, aplicável ao modelo, para cada valor exigido do modelo marcado completo

Sem a chave, o catálogo nacional fica indisponível. Isso é o resultado esperado.

## Carga

1. Aplicar a migração nova.
2. Carregar a emenda vigente do ROTAER. A conferência conta aeródromos de avião e verifica que um heliponto conhecido da emenda não entra na lista oferecida.
3. Carregar o extrato vigente do RAB e ordenar pelo número de aeronaves de cada modelo.
4. Pesquisar fontes para cada candidato e campo. Registrar tipo de fonte, publicador, referência, data de publicação e consulta, modelo/variante e perfil; para POH/AFM, registrar também revisão/edição e página/tabela.
5. Conferir que velocidade e consumo formam o mesmo perfil nominal de cruzeiro e que combustível é utilizável, sem a parcela inutilizável. Entre fontes aplicáveis conflitantes, selecionar a mais recente mesmo se menos específica, guardar a divergência e a incerteza e não fazer média. Sem data ou aplicabilidade verificável, manter o campo indisponível.
6. Auditar toda a semente pela mesma regra. Uma referência livre sem publicador, data ou aplicabilidade não torna o campo completo. Preservar valores antigos, mas não os usar até haver fonte verificável; não criar exceção por modelo.
7. Carregar somente dados revisados pelo processo de semente. Verificar que a seleção filtra completude antes de ordenar e cortar nos 30, que modelos incompletos e completos além do limite não aparecem e que nenhum deles é aceito por envio direto.
8. Em modelo com fonte secundária, confirmar o rótulo de estimativa didática e a referência de cada grandeza na seleção, resultado e PDF.
9. Sem extrato RAB vigente, verificar resposta `indisponivel`, lista de modelos vazia e recusa de novos planos com aeronave.

Não colar chave, senha nem números técnicos de aeronave neste arquivo. A carga guarda os valores selecionados no registro do modelo e cada citação na proveniência estruturada por campo.

## Rota

1. Entrar com um piloto.
2. Pedir um par cujo direto caiba nos limites dos dados técnicos selecionados. A rota tem um trecho.
3. Pedir um par cujo direto não caiba na reserva de 30 minutos. A rota tem escala, cada trecho cabe na reserva, e o critério mostrado é o menor tempo de voo.
4. Abrir o PDF e achar os trechos, a hipótese de reabastecimento e a frase de que não é autorização.
5. Repetir sem a publicação vigente: a tela identifica a lista local como incompleta e não nacional; tentar enviar um plano e confirmar que o servidor o recusa por catálogo nacional indisponível.

## O que não conferir aqui

Isolamento, senha e bloqueio já têm quickstart no plano direto. Esta conferência não os reabre.
