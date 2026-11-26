---
title: 'Pesquisa de domínio: Dados oficiais de aeronaves do MVP'
type: 'domain'
topic: 'Dados oficiais de aeronaves do MVP'
decision: 'Quais modelos podem entrar no MVP com dados técnicos oficiais e verificáveis'
source: 'native research'
status: draft
preset: 'standard'
validation: 'normal'
created: '2026-11-24'
updated: '2026-11-24'
---

# Pesquisa de domínio: Dados oficiais de aeronaves do MVP

**Decisão que esta pesquisa apoia:** Quais modelos podem entrar no MVP com dados técnicos oficiais e verificáveis.

_As seções serão acrescentadas conforme o plano aprovado; o resumo executivo será escrito por último e colocado no início._

## RAB: fonte atual, esquema e limites

A ANAC publica o extrato do RAB em CSV e JSON; o arquivo CSV oficial respondeu em 2026-11-24 com a linha de atualização dessa data e `Last-Modified` do mesmo dia [1][2]. A data do próprio arquivo ainda não foi confirmada por uma medição independente: a captura independente da Quantilica é de 2026-11-10 [5]. O extrato contém modelo, fabricante, classificação, PMD e também colunas de proprietários e operadores; estas últimas não devem ser importadas nem exibidas [3][5].

A documentação da ANAC descreve `CD_TIPO` como código de habilitação de piloto, não como classificação universal da aeronave. `CD_CLS` e `TP_POUSO` são candidatos melhores para a triagem; a planilha oficial de homologação por modelo fornece modelo, fabricante, classe e categoria, mas foi criada em 2022 e não substitui o RAB atual nem o POH/AFM [6][18]. A unidade do `NR_PMD` continua sem confirmação documental; não usar esse valor numérico para decidir o limite de 5.670 kg [7][20].

O usuário definiu que a ordem de frota conte somente registros com `CD_INTERDICAO=N`; os códigos `U` e `Z`, embora descritos pela ANAC como ultraleve e experimental em situação normal, ficam excluídos [23]. A lista anterior com `N/U/Z` foi supersedida [17]. Reprocessei o extrato atual usando somente campos técnicos e o novo status, mantendo os filtros provisórios de pouso e motor: 10.040 registros e 652 pares fabricante/modelo [30]. A lista resultante serve apenas para ordenar a busca de manuais; não prova classe avião nem PMD aprovado ≤ 5.670 kg. A unidade do PMD e a classificação final continuam em aberto, e a contagem aguarda verificação independente.

## POH/AFM: primeira rodada, candidatos 1–5

Não foi confirmado nenhum POH/AFM de variante exata com edição/revisão e páginas/tabelas para os campos necessários entre os cinco primeiros candidatos [24][25][26]. A Cirrus lista publicações distintas para o SR22, mas a listagem não casa a configuração do candidato nem fornece dados de cálculo; os outros resultados oficiais encontrados foram índice de downloads ou portaria regulatória, não manuais de desempenho [24][25][26]. Nenhum valor será preenchido por estimativa ou fonte secundária. “Não encontrado” descreve somente as fontes públicas pesquisadas, não a inexistência do manual.

Uma verificação independente também não encontrou fonte pública oficial que reúna, para uma configuração e série aplicáveis, o manual/revisão e todos os campos obrigatórios [31]–[35]. Há dados parciais em excerto de AFM e especificação de tipo, mas não o conjunto exigido; manuais da Cirrus e Piper são serializados e/ou têm dados de peso e balanceamento individualizados [31][33][34][35]. A catalogação ainda não informa números de série nem um perfil comum de cruzeiro para parear velocidade e consumo.

## POH/AFM: candidatos 6–10

Não foi confirmado manual oficial de variante exata com revisão e páginas/tabelas para EMB-201A, AT-402B, Cessna 152, EMB-202A ou PA-46-500TP. As pistas secundárias encontradas para o AT-402B e PA-46 não foram usadas como evidência nem para preencher dados [29]. Para todos os cinco, os seis campos permanecem sem verificação; a busca negativa é limitada às fontes públicas consultadas.

## POH/AFM: candidatos 11–15

Também não foi confirmado manual de variante exata e páginas/tabelas para A188B, EMB-810D, EMB-500, Beech 58 ou Beech A36. A busca consultou fontes oficiais FAA/ANAC e encontrou apenas índices gerais e um resultado DRS sem conteúdo de manual utilizável [27][28]. Todos os campos permanecem sem verificação e os cinco modelos ficam em espera; a ausência em fontes públicas pesquisadas não prova inexistência de manual.

## POH/AFM: candidatos 16–20

Os candidatos 16 (Cessna 208B), 17 (EMB-711ST), 18 (Cessna 182P) e 20 (B200GT) atendem ao filtro avião/PMD ≤ 5.670 kg segundo registros ou especificações ANAC [44]–[49][52]. O EMB-505, rank 19, excede o limite com PMD de 8.150 kg e é excluído [50][51]. Para os quatro elegíveis, foram encontrados números de manual ou alterações temporárias em algumas fontes, mas não o POH/AFM completo aplicável e as páginas/tabelas para todos os campos [45][46][48]. Portanto, nenhum desses modelos pode ser marcado completo.

## POH/AFM: candidatos 21–25

Registros e especificações ANAC confirmam que EMB-810C, EMB-712, Cessna 525, EMB-711C e C90GTi são aviões com PMD aprovado dentro do limite de 5.670 kg [36]–[43]. Isso permite mantê-los na ordem de busca, mas não os torna completos. Os manuais de operação aplicáveis não foram obtidos; em alguns casos a especificação apenas exige um Manual de Voo ou informa um identificador sem revisão atual [37][39][40][42]. Peso vazio, bagagem, combustível utilizável e velocidade/consumo pareados de cruzeiro continuam sem páginas/tabelas de POH/AFM.

### Fontes

| Ref. | Fonte | Data/publicação |
|---|---|---|
| [1] | [Página de dados abertos RAB da ANAC](https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro) | Modificada em 2026-04-07 |
| [2] | [CSV oficial do RAB](https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv) | Atualizado em 2026-11-24, segundo o próprio arquivo |
| [3][6][23] | [Metadados do RAB histórico](https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro-historico/metadados-registro-aeronautico-brasileiro-historico) | Modificados em 2026-03-19 |
| [17] | Agregação local do CSV RAB, sem dados de proprietários/operadores | Acesso em 2026-11-24; triagem preliminar, não verificada independentemente |
| [18] | [Tabela ANAC de categorias de homologação por modelo](https://www.gov.br/anac/pt-br/sistemas/rab/arquivos/tabela-de-categorias-de-homologacao-por-modelo-de-aeronave.xlsx) | Criada em 2022-05-11 |
| [5] | [Quantilica Hub: captura independente do RAB](https://quantilica.com/hub/anac/rab-atual) | 2026-11-10 |
| [7] | [ANAC: RBAC 21](https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-21) | Modificado em 2026-10-22 |
| [20] | [Guia ANAC de acesso a informações de aeronaves](https://www.gov.br/anac/pt-br/sistemas/rab/arquivos/guia-de-acesso-a-informacoes-de-aeronaves-brasileiras) | Criado em 2022-08-02 |
| [24] | [Loja oficial Cirrus: AFM 44765-001](https://store.cirrusaircraft.com/sr22-afm-44765-001%2C-perspective-touch-/5637446858.p) | Acesso em 2026-11-24 |
| [25] | [Air Tractor: Downloads](https://airtractor.com/downloads/) | Página indicada como atualizada em 2025-05-07 |
| [26] | [ANAC: Portaria nº 14.009](https://www.anac.gov.br/assuntos/legislacao/legislacao-1/portarias/2024/portaria-14009) | 2024-03-05 |
| [27] | [FAA: Aircraft Handbooks & Manuals](https://www.faa.gov/regulations_policies/handbooks_manuals/aircraft) | Página indica atualização em 2013-02-27 |
| [28] | [FAA DRS: resultado de busca](https://drs.faa.gov/browse/excelexternalwindow/drsdocid158639337320230202213157.0001) | Acesso em 2026-11-24; conteúdo do manual não recuperado |
| [29] | [ANAC: Portaria nº 11.610](https://www.anac.gov.br/assuntos/legislacao/legislacao-1/portarias/2023/portaria-11610) | 2023-06-13; publicação regulatória, não manual |
| [30] | Agregação técnica local do CSV oficial RAB [2], status `N` | Acesso em 2026-11-24; filtros de pouso/motor provisórios, aguardando verificação independente |
| [31] | [Cirrus: POH SR22 13772-006](https://store.cirrusaircraft.com/sr22-faa-poh-13772-006%2C-perspective-/5637329128.p) | Acesso em 2026-11-24 |
| [32] | [Air Tractor: aviso do portal de proprietários](https://airtractor.com/news/2018/06/air-tractor-aircraft-parts-manuals-now-updated-biannually/) | 2018-06; acesso em 2026-11-24 |
| [33] | [NTSB: excerto AFM AT-502B](https://data.ntsb.gov/Docket/Document/docBLOB?ID=15340680&FileExtension=pdf&FileName=10%20-%20Air%20Tractor%20AT-502B%20Airplane%20Flight%20Manual%20(Excerpts)-Rel.pdf) | AFM reproduzido emitido em 2016-03-18; acesso em 2026-11-24 |
| [34] | [ANAC: especificação de tipo EA-7104-12](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-7104-12p.pdf) | 2018-08-03 |
| [35] | [Piper: catálogo oficial de publicações](https://www.piper.com/wp-content/uploads/2026/06/753-755-Owner-Publications-Catalog-3-3.pdf) | Acesso em 2026-11-24 |
| [36] | [ANAC: registro EMB-810C](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetail.asp?ProdCodi=0001065) | Acesso em 2026-11-24 |
| [37] | [ANAC: especificação EA-7501-06](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-7501-06p.pdf) | 2018-05-03 |
| [38] | [ANAC: registro EMB-712](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetailE.asp?ProdCodi=0001057) | Acesso em 2026-11-24 |
| [39] | [ANAC: especificação EA-7801-01](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-7801-01p.pdf) | 1988-08 |
| [40] | [ANAC: especificação EA-9304-20](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-9304-20i.pdf) | Acesso em 2026-11-24 |
| [41] | [ANAC: registro EMB-711C](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetailE.asp?ProdCodi=0001054) | Acesso em 2026-11-24 |
| [42] | [ANAC: especificação EA-7502-07](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-7502-07p.pdf) | 2018-05-03 |
| [43] | [ANAC: registro C90GTi](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetailE.asp?ProdCodi=0004295&Isent=S) | Acesso em 2026-11-24 |
| [44] | [ANAC: registro Cessna 208B](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetailE.asp?ProdCodi=0000148) | Acesso em 2026-11-24 |
| [45] | [ANAC: especificação EA-8805-03](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-8805-03i.pdf) | Acesso em 2026-11-24 |
| [46] | [Textron Aviation: Recent Publications](https://ww2.txtav.com/TechnicalPublications/RecentPubs) | Acesso em 2026-11-24 |
| [47] | [ANAC: registro EMB-711ST](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetail.asp?ProdCodi=0001055) | Acesso em 2026-11-24 |
| [48] | [ANAC: especificação EA-7502-07](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-7502-07p.pdf) | Acesso em 2026-11-24 |
| [49] | [ANAC: registro Cessna 182P](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetail.asp?ProdCodi=0000099) | Acesso em 2026-11-24 |
| [50] | [ANAC: registro EMB-505](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetailE.asp?ProdCodi=0004389) | Acesso em 2026-11-24 |
| [51] | [ANAC: especificação EA-2009T12](https://sistemas.anac.gov.br/certificacao/Produtos/Espec/EA-2009T12p.pdf) | Acesso em 2026-11-24 |
| [52] | [ANAC: registro B200GT](https://sistemas.anac.gov.br/certificacao/Produtos/ProdutoDetailE.asp?ProdCodi=0004289&Isent=S) | Acesso em 2026-11-24 |
