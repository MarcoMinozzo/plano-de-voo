# Quickstart: Rota com escalas

Conferência depois da implementação. Não substitui `tasks.md`.

## Pré-requisitos

- O plano direto já sobe, como em `documentacao/operacao.md`
- Chave do AISWEB no ambiente, para a carga real do ROTAER e do pôr do sol
- Extrato público do RAB disponível para quem opera, sem copiar o arquivo para o repositório se ele trouxer dado que não seja o catálogo de modelos

Sem a chave, o catálogo nacional fica indisponível. Isso é o resultado esperado.

## Carga

1. Aplicar a migração nova.
2. Carregar a emenda vigente do ROTAER. A conferência conta aeródromos de avião e verifica que um heliponto conhecido da emenda não entra na lista oferecida.
3. Carregar o extrato do RAB. A conferência ordena pela frota.
4. Rodar `python -m servidor.manuais`. A saída diz quantos arquivos gravou e nomeia cada arquivo recusado com o campo. Os 20 modelos de [research.md](./research.md#os-20-modelos) ficam `gravado`. Um experimental, como o RV-10, continua sem manual e é recusado pelo nome.
5. Planejar um voo com um modelo de pistão e outro de turboélice. A ficha mostra a fonte com documento e página, e o peso do turboélice usa a massa por galão do manual.

Não colar chave, senha nem número de manual neste arquivo.

## Rota

1. Entrar com um piloto.
2. Pedir um par cujo direto caiba no manual. A rota tem um trecho.
3. Pedir um par cujo direto não caiba na reserva de 30 minutos. A rota tem escala, cada trecho cabe na reserva, e o critério mostrado é o menor tempo de voo.
4. Abrir o PDF e achar os trechos, a hipótese de reabastecimento e a frase de que não é autorização.
5. Repetir sem a publicação vigente e ver o catálogo indisponível, sem coordenada nova.

## O que não conferir aqui

Isolamento, senha e bloqueio já têm quickstart no plano direto. Esta conferência não os reabre.
