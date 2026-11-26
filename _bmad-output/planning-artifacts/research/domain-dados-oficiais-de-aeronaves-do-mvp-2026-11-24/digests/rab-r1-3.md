# Digest: códigos observados no RAB atual — rodada 1

**Acesso:** 2026-11-24 · o arquivo declara atualização em 2026-11-24.

## Conclusões observadas no CSV

- **[13] `TP_POUSO` distingue categorias de pouso**, incluindo “POUSO CONVENCIONAL” (26.546 registros), “HELICOPTERO” (3.420), “ANFIBIO” (242), “GIROCOPTERO” (101), “DRONE (RPAS)” (82), “POUSO EM TERRA” (18) e “POUSO NA AGUA” (10). Os valores foram contados no arquivo completo, sem filtrar aeronavegabilidade; não são a frota final por modelo. **Confiança: alta. Classe: distribuição do conjunto.**
- **[14] `TP_MOTOR` separa motores convencionais, jato/turbofan, turbo-hélice, turboeixo, ausência de motor, drones e motor elétrico.** O conjunto inclui 920 registros com “SEM MOTOR”, portanto uma filtragem apenas por `TP_POUSO` não basta para excluir planadores. **Confiança: alta. Classe: distribuição do conjunto.**
- **[15] `CD_CLS` contém códigos estruturados** como `L1P`, `L2J`, `L2P`, `L2T`, `L1T`, `H1T`, `H2T`, `L00`, `H1P` e `A1P`. Seus valores precisam ser interpretados com a documentação oficial antes de usar o campo como filtro. **Confiança: alta. Classe: distribuição do conjunto.**

## Fonte

13–15. ANAC, CSV público RAB, metadados HTTP e agregação local das colunas `TP_POUSO`, `TP_MOTOR` e `CD_CLS`; acesso em 2026-11-24: https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv

## Limite da leitura

O processamento contou apenas categorias e códigos técnicos; colunas de titulares e operadores não foram impressas. A tabela não representa um ranking válido para o MVP: falta definir filtros de status, classe de aeronave e PMD com base em fontes oficiais, e a contagem deve ser agregada por variante/modelo certificado.
