# Digest: lista de busca com status RAB N somente

**Acesso:** 2026-11-24 · lista de busca, não seleção final do MVP.

## Método

O CSV oficial do RAB respondeu `Last-Modified: Tue, 24 Nov 2026 05:39:46 GMT` e sua linha de atualização informa 2026-11-24. Reprocessei em fluxo, agregando somente `DS_MODELO` e `NM_FABRICANTE`, sem persistir nem imprimir dados de proprietários/operadores. Conforme decisão do usuário, considerei somente `CD_INTERDICAO=N`. Mantive os filtros técnicos provisórios da lista anterior: pouso convencional, anfíbio, na água ou em terra; motor informado e diferente de “SEM MOTOR” ou “DRONE”. Ordenei por contagem decrescente e, em empate, `DS_MODELO` crescente, com fabricante como desempate secundário.

Resultado dessa triagem: **10.040 registros e 652 pares fabricante/modelo**. Distribuição de pouso: convencional 9.999, anfíbio 23, em terra 17 e na água 1. Os códigos `CD_CLS` observados com mais frequência foram L1P (4.906), L2J (1.628), L1T (1.412), L2P (1.060), L2T (938), L1J (37), L3J (18), L1E (17), A1T (13), A1P (10) e S1P (1); sem interpretar esses códigos como classificação de avião nesta triagem.

## Primeiros 40 pares por contagem

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
16. CESSNA AIRCRAFT — 208B: 122
17. NEIVA — EMB-711ST: 122
18. CESSNA AIRCRAFT — 182P: 121
19. EMBRAER — EMB-505: 119
20. TEXTRON AVIATION — B200GT: 96
21. EMBRAER — EMB-810C: 84
22. NEIVA — EMB-712: 83
23. CESSNA AIRCRAFT — 525: 82
24. NEIVA — EMB-711C: 82
25. HAWKER BEECHCRAFT — C90GTI: 81
26. BEECH AIRCRAFT — C90A: 80
27. CIRRUS DESIGN — SR22T: 80
28. PIPER AIRCRAFT — PA-46-350P: 78
29. AIR TRACTOR — AT-502A: 76
30. BEECH AIRCRAFT — F33A: 74
31. NEIVA — EMB-720D: 74
32. PIPER AIRCRAFT — PA-46R-350T: 66
33. EMBRAER — EMB-810D: 65
34. CESSNA AIRCRAFT — 172M: 63
35. BEECH AIRCRAFT — V35B: 63
36. CESSNA AIRCRAFT — 510: 62
37. TEXTRON AVIATION — 525: 62
38. HAWKER BEECHCRAFT — G58: 61
39. AIR TRACTOR — AT-802A: 60
40. BOEING COMPANY — 737-8 MAX: 59

## Limites

Esta triagem não prova que os modelos são aviões pequenos. `TP_POUSO` e motor não excluem com segurança aeronaves de outras classes; vários itens podem exceder 5.670 kg. O campo `NR_PMD` continua sem unidade confirmada. A lista serve apenas para ordenar a busca inicial; elegibilidade exige confirmar avião, PMD aprovado ≤ 5.670 kg e POH/AFM oficial aplicável com todos os campos.

## Fonte

30. Agregação local técnica do CSV oficial da ANAC [2], acesso em 2026-11-24; filtro `CD_INTERDICAO=N` e regras provisórias acima. Não é confirmação independente da contagem.
