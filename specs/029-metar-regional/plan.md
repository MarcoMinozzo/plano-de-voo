# Plano de Implementação: METAR regional próximo ao aeródromo

**Branch**: `029-metar-regional` | **Data**: 2026-11-26 | **Spec**: [spec.md](./spec.md)

**Entrada**: `specs/029-metar-regional/spec.md`

## Resumo

Manter o METAR direto quando publicado; na ausência dele, procurar no AWC o METAR mais próximo dentro de 50 NM e exibir explicitamente estação, indicativo, distância e horário. Consultar o TAF do aeródromo de forma independente, sem substituí-lo pelo de outra localidade. Registrar falhas técnicas sem expor credenciais.

## Contexto técnico

**Linguagem**: Python 3.10+; Jinja para apresentação.

**Dependências**: Flask, requests, SQLAlchemy e ReportLab já existentes. Nenhuma dependência nova.

**Armazenamento**: Resultado meteorológico continua no JSON salvo do plano; sem tabela ou migração nova.

**Testes**: pytest focado em `servidor/tempo.py`, apresentação HTML e PDF; execução manual no plano atual com SBBU, SDFD e SBEK.

**Plataforma**: Serviço Flask local e navegadores desktop/móveis.

**Metas**: No máximo uma consulta regional adicional por aeródromo sem METAR direto; manter a atualização de METAR/TAF ao abrir o relatório salvo, sem persistir os dados atualizados nem alterar rota/cálculos.

**Restrições**:
- AWC permanece a única fonte meteorológica.
- O limite de elegibilidade é 50 NM, confirmado pelo usuário.
- A distância geográfica exata filtra a lista retornada pelo retângulo de busca; arredondamento é somente para exibição.
- METAR regional deve ser distinguido do aeródromo de referência em HTML, fontes e PDF.
- TAF é consultado pelo indicativo do aeródromo, independentemente do METAR; não há TAF regional.
- Falhas de rede, HTTP ou JSON são registradas sem credenciais; dados ausentes permanecem indisponíveis.
- Abrir um plano salvo atualiza METAR/TAF somente para a resposta da página; não modifica o JSON persistido nem os cálculos.
- Cálculo de distância fica no servidor. Nenhum dado sintético ou inferido pode aparecer como observação real.
- Mantém-se o aviso de uso didático; não é ferramenta operacional de despacho.

**Escopo**: Aeródromos usados pelo plano e suas coordenadas ROTAER. Uma estação METAR regional por aeródromo, escolhida pelo menor arco geográfico entre as observações AWC elegíveis; empate resolvido pelo indicativo em ordem lexical.

## Verificação da Constituição

| Princípio | Resultado | Resposta de projeto |
|---|---|---|
| I. Especificação antes do código | PASS | Esta especificação, plano, modelo, contrato e quickstart precedem a implementação. |
| II. Limite educacional | PASS | O relatório identifica a estação regional e mantém o aviso didático; não declara condição da pista nem autoriza voo. |
| III. Cálculo no servidor | PASS | Busca, distância, prioridade e associação ocorrem no servidor; HTML/PDF apenas apresentam o resultado salvo. |
| IV. Unidades e fonte explícitas | PASS | Exibir estação, fonte AWC, horário UTC e distância NM; não inventar dados ausentes. |
| V. Pilha e fonte meteorológica | PASS | Reutilizar AWC e dependências atuais. Nenhum fallback de provedor ou credencial adicional. |

Nenhuma exceção constitucional ou migração de banco é necessária.

## Pesquisa e decisões técnicas

1. Consultar primeiro `/api/data/metar` pelo indicativo do aeródromo. Quando não houver METAR direto, consultar o mesmo produto com `bbox` em torno das coordenadas ROTAER, dimensionado para abranger 50 NM. O formato AWC usa `(lat0, lon0, lat1, lon1)` e admite no máximo três casas decimais; cada resultado é filtrado pela distância geodésica exata.
2. O payload AWC fornece `icaoId`, `name`, `lat`, `lon`, `reportTime` e `rawOb`. Persistir esses metadados junto ao METAR, com o indicativo do aeródromo de referência, estado direto/regional e distância.
3. Consultar `/api/data/taf` independentemente pelo indicativo do aeródromo. Resultado vazio ou falha do METAR não encerra a rotina de TAF.
4. Isolar tratamento de resposta vazia de erros HTTP, rede ou JSON. Registrar falhas com identificador do aeródromo e produto, sem URL sensível nem credenciais. Um produto pode ficar indisponível enquanto o outro permanece disponível.
5. Preservar a atualização de METAR/TAF já feita ao abrir um plano salvo. A consulta é somente de leitura: atualiza a apresentação da requisição, sem gravar sobre o snapshot persistido ou alterar rota e cálculos.

## Estrutura do projeto

### Documentação

```text
specs/029-metar-regional/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── meteorologia-relatorio.md
├── quickstart.md
└── tasks.md
```

### Código

```text
servidor/tempo.py
servidor/planos_consulta.py
servidor/pdf_plano.py
servidor/pdf_layout.py
templates/plano.html
tests/test_tempo.py
tests/test_tela_piloto.py
tests/test_rota_pdf.py
```

**Decisão estrutural**: Estender a integração atual de boletins. `meteorologia_rota` já percorre os aeródromos distintos da rota; cada boletim guardará o indicativo da localidade consultada separado do indicativo da estação que publicou o METAR. O JSON existente mantém os dados de forma reproduzível.

## Complexidade

Sem nova dependência, serviço, tabela, migração ou violação constitucional.
