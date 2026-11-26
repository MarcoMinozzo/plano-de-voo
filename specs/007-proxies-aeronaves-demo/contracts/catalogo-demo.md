# Contract: Catálogo e planos DEMO

## Elegibilidade e seleção

- O modo normal retorna apenas modelos com fontes técnicas oficiais completas e não aceita fontes sintéticas.
- O modo DEMO pode retornar até 40 perfis: os 20 genéricos existentes e até 20 proxies aprovados.
- Não retornar perfil sintético sem evidência aplicável e metadados completos para todos os campos técnicos exigidos pelo cálculo.
- O cadastro selecionado deve preservar os valores atuais e os metadados de cada fonte usados pelo cálculo.

## Procedência apresentada

Para cada campo sintético, a tela, o resultado e o PDF devem informar:

- valor e unidade;
- intervalo admissível;
- publicador(es), referência(s), modelo/variante e aplicabilidade;
- método de geração e versão/semente;
- incerteza;
- data de consulta e indicação “data editorial não se aplica” quando `data_publicacao` for nula.

Cada página/resultado/PDF que usa esses perfis deve declarar que são dados sintéticos de demonstração, não representam dados certificados de uma aeronave real e não autorizam voo.
Ao exibir um proxy, usar o rótulo “DEMO — proxy sintético”, identificar o modelo associado somente como alvo de teste e declarar que os valores não são fatos nem dados aprovados para aquele modelo.

## ROTAER e fontes meteorológicas

- A criação de plano DEMO exige emenda ROTAER oficial vigente e aeródromos vinculados a ela.
- A transferência para DEMO abrange somente os registros oficiais da emenda vigente; nunca copia pilotos, planos ou dados de outras tabelas.
- A aplicação DEMO não conecta ao banco normal em runtime.
- METAR/TAF, vento, radar, carta visual e pôr do sol permanecem sob as integrações oficiais existentes; erro, ausência de cobertura ou ausência de credenciais resulta em indisponibilidade explícita, nunca em valor inventado.

## Compatibilidade e isolamento

- O catálogo normal continua limitado a 30 modelos.
- Nenhum proxy aparece no catálogo normal, em seleções ou em cálculos normais.
- O ambiente DEMO continua exigindo banco PostgreSQL dedicado e `APP_ENV=development`; não existe fallback para `DATABASE_URL`.
- A carga DEMO é idempotente e não apaga planos ou dados anteriores.
