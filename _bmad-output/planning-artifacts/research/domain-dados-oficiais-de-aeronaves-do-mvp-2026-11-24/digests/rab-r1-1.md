# Digest: extrato RAB oficial — rodada 1

**Acesso:** 2026-11-24

## Conclusões verificadas

- **[1] Existe um extrato público oficial do RAB em CSV e JSON.** A página de dados abertos da ANAC lista ambos os formatos e fornece o CSV em `https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv`. A página estava modificada em 2026-04-07. **Confiança: alta. Classe: disponibilidade/fonte.**
- **[2] O CSV estava atualizado na data desta pesquisa.** A resposta do arquivo foi HTTP 200, com `Last-Modified: 2026-11-24 05:39:46 GMT`; a primeira linha informa `Atualizado em: 2026-11-24`. **Confiança: alta. Classe: atualidade do conjunto.**
- **[3] O cabeçalho contém campos suficientes para agrupar por classificação, modelo, fabricante e PMD:** `CD_TIPO`, `DS_MODELO`, `NM_FABRICANTE`, `NR_PMD`, entre outros. O arquivo também contém colunas pessoais (`PROPRIETARIOS`, `OPERADORES`); qualquer processamento deve agregar apenas campos técnicos e não mostrar nem persistir essas colunas. **Confiança: alta. Classe: esquema/privacidade.**

## Fontes

1. ANAC, “Registro Aeronáutico Brasileiro - RAB”, página modificada em 2026-04-07; acesso em 2026-11-24: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro
2. ANAC, CSV público RAB, metadados HTTP e linha de atualização observados em 2026-11-24: https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv

## Próximas pistas e lacunas

- A página oficial lista uma tabela auxiliar de categorias de homologação por modelo e um guia de acesso ao RAB; verificar se ajudam a classificar os tipos e interpretar `NR_PMD`.
- Ainda falta confirmar em documentação oficial o significado/unidade de cada coluna relevante e a regra segura para separar aviões dos demais tipos do extrato.
