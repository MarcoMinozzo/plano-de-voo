# Verificação independente: extrato RAB

**Acesso:** 2026-11-24 · validação normal

- **Disponibilidade do extrato:** confirmada pela página oficial da ANAC; a página lista CSV e JSON. A captura independente da Quantilica confirma que um terceiro acompanha o conjunto da ANAC, mas não confirma separadamente os dois formatos. **Status: verificado; confiança alta.**
- **Atualização em 2026-11-24:** o endpoint oficial respondeu com `Last-Modified` e a linha de atualização nessa data. A captura independente da Quantilica é de 2026-11-10 e, portanto, não confirma a atualização de hoje. **Status: não verificado independentemente; confiança média.** Preservar a data como metadado informado pela própria ANAC.
- **Colunas técnicas e de titular/operador:** ANAC e a captura independente da Quantilica corroboram a presença de campos de classe, modelo, fabricante, PMD, proprietários e operadores. A interpretação de `CD_TIPO` ainda requer cautela: a documentação o descreve como código ligado à habilitação/classe, não como classificação universal do tipo de aeronave. **Status: verificado; confiança alta.**

## Fontes adicionais

4. ANAC, metadados históricos do RAB, modificado em 2026-03-19: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro-historico/metadados-registro-aeronautico-brasileiro-historico
5. Quantilica Hub, captura independente “RAB Atual (ANAC - Dados Abertos)”, datada de 2026-11-10: https://quantilica.com/hub/anac/rab-atual

## Consequência

O arquivo RAB é utilizável para obter a lista e a ordenação de frota, mas o código de classe não deve ser interpretado sem documentação oficial. Ao processar o CSV, descartar colunas de proprietários e operadores e emitir somente agregados por modelo/fabricante/classe.
