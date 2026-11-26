# Verificação: códigos e contagens RAB

**Acesso:** 2026-11-24 · validação normal

- **`TP_POUSO`:** ANAC define o campo como tipo de pouso; a leitura do CSV reproduziu os valores e contagens registrados no digest, além de 4.759 linhas sem valor. **Status: reproduzido na fonte primária; não verificado por medição independente.**
- **`TP_MOTOR`:** ANAC define o campo como tipo de motor; o CSV reproduz as categorias e as 920 linhas “SEM MOTOR”, além de 4.759 vazias. **Status: reproduzido na fonte primária; não verificado por medição independente.**
- **`CD_CLS`:** ANAC documenta classificação baseada em pouso, motor e quantidade de motores, conforme RBAC 21. As descrições de produto ANAC ajudam a interpretar exemplos; tradução de H1T varia em páginas em inglês, então usar a descrição em português como referência. **Status: significado geral verificado pela fonte primária; códigos individuais ainda precisam de conferência.**
- **Contagens:** os números vieram do mesmo CSV oficial e foram reproduzidos, não de uma segunda medição. O painel ANAC não expôs contagem utilizável; a Quantilica replica o conjunto ANAC e a captura é anterior. **Status: não verificado independentemente.**

## Fontes

13. ANAC, CSV público RAB, atualizado em 2026-11-24: https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv
14. ANAC, metadados RAB histórico, modificado em 2026-03-19: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro-historico/metadados-registro-aeronautico-brasileiro-historico
15. ANAC, painel RAB, modificado em 2026-06-10: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro/painel-registro-aeronautico-brasileiro-rab
16. Quantilica Hub, snapshot RAB datado de 2026-11-10: https://quantilica.com/hub/anac/rab-atual
