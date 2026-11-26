# Digest: primeira lista para pesquisa de manuais

**Acesso:** 2026-11-24 · lista preliminar, não é seleção final do MVP.

> **Histórico supersedido:** esta primeira lista agregava status `N/U/Z`. Após decisão do usuário de contar somente `N`, use [candidates-r1-3.md](./candidates-r1-3.md) como ordem de busca vigente.

## Método provisório

No CSV RAB vigente, agreguei somente `DS_MODELO` e `NM_FABRICANTE`, sem ler/imprimir proprietários ou operadores. Para formar uma lista de busca, considerei registros com `CD_INTERDICAO` igual a `N`, `U` ou `Z`; `TP_POUSO` igual a `POUSO CONVENCIONAL`, `ANFIBIO`, `POUSO NA AGUA` ou `POUSO EM TERRA`; e motor informado, diferente de “SEM MOTOR” ou “DRONE”. O filtro resulta em 14.291 registros e 3.524 pares fabricante/modelo.

Esse filtro é apenas uma triagem de busca: a documentação de `CD_INTERDICAO` precisa ser aplicada corretamente, a interpretação de pouso não foi validada como classificação universal de avião, o PMD do CSV ainda não tem unidade confirmada e a lista não exclui variantes acima de 5.670 kg. Não usar estes números para gravar a semente ou declarar elegibilidade.

## Primeiros 30 pares fabricante/modelo por contagem

1. CIRRUS DESIGN — SR22: 515
2. AIR TRACTOR — AT-502B: 356
3. EMBRAER — EMB-203: 326
4. PIPER AIRCRAFT — PA-34-220T: 219
5. NEIVA — EMB-202: 204
6. NEIVA — EMB-201A: 197
7. AIR TRACTOR — AT-402B: 173
8. CESSNA AIRCRAFT — 152: 167
9. EMBRAER — EMB-202A: 166
10. PIPER AIRCRAFT — PA-46-500TP: 162
11. CESSNA AIRCRAFT — A188B: 154
12. NEIVA — EMB-810D: 153
13. EMBRAER — EMB-500: 137
14. BEECH AIRCRAFT — 58: 130
15. BEECH AIRCRAFT — A36: 128
16. TRIKE ICAROS — ADVENTURE: 124
17. CESSNA AIRCRAFT — 208B: 122
18. NEIVA — EMB-711ST: 122
19. CESSNA AIRCRAFT — 182P: 121
20. EMBRAER — EMB-505: 119
21. TEXTRON AVIATION — B200GT: 96
22. EMBRAER — EMB-810C: 84
23. NEIVA — EMB-712: 83
24. CESSNA AIRCRAFT — 525: 82
25. NEIVA — EMB-711C: 82
26. HAWKER BEECHCRAFT — C90GTI: 81
27. BEECH AIRCRAFT — C90A: 80
28. CIRRUS DESIGN — SR22T: 80
29. PIPER AIRCRAFT — PA-46-350P: 78
30. AIR TRACTOR — AT-502A: 76

## Fonte e confiança

17. ANAC, CSV público RAB, atualizado em 2026-11-24; contagem local dos campos técnicos citados: https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv

**Confiança:** média para a lista preliminar reproduzível da fonte; baixa para interpretá-la como ordem oficial de aeronaves pequenas antes de resolver as lacunas acima. Estas são contagens de registros da triagem, não ainda de aeronaves completas nem do MVP.
