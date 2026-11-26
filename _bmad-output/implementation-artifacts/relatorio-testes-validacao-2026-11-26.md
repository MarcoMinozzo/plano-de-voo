# Relatório didático de testes e validação

**Data:** 26 de novembro de 2026  
**Resultado geral:** aprovado nos testes automatizados executados  
**Escopo:** restauração dos gates de validação e regressão visual do logo nas telas de entrar e cadastro.

## Resumo executivo

A suíte completa terminou com **136 testes aprovados e nenhum teste falho**. A cobertura foi de **86,56%**, acima do mínimo configurado de 27%. O gate de mutação atingiu **68,37%**, acima do piso de 56%. Também passaram a verificação de complexidade e tamanho dos módulos, o Ruff e a verificação de whitespace do Git.

Esses resultados dão boa evidência de que os comportamentos cobertos continuam funcionando. Eles **não** substituem a validação de dados oficiais, licenças de mapas ou inspeções manuais que ainda estão pendentes.

## Resultados, explicados

| Verificação | O que ela procura | Resultado |
|---|---|---|
| Suíte completa: `env -u DATABASE_URL -u DATABASE_URL_TESTE uv run --no-sync pytest` | Executa os testes funcionais e os gates automatizados do projeto. As variáveis são removidas para que a configuração de testes use o banco descartável, não um banco de produto. | **136 passaram**, em 214,60 s. Nenhum falhou. |
| Cobertura da suíte | Mede quantas linhas de código foram executadas pelos testes; não mede, sozinha, se todos os requisitos de negócio estão corretos. | **86,56%**: 2.150 instruções medidas, 289 não cobertas. O mínimo configurado é 27%. |
| Gate de mutação | Faz pequenas alterações artificiais no código e verifica se os testes percebem essas mudanças. Uma mutação sobrevivente indica uma oportunidade de teste, não necessariamente um defeito no produto. | **348 eliminadas / 509 = 68,37%**. Piso: 56%. Sem mutantes sem teste, ignorados, suspeitos ou com timeout. |
| Forma dos módulos | Verifica limites de complexidade ciclomática e tamanho definidos pelo projeto. | **Aprovado** na suíte completa; limites mantidos em 23 e 462 linhas. |
| Ruff | Procura problemas estáticos de estilo e erros comuns nos módulos Python alterados. | **Aprovado**: “All checks passed!”. |
| `git diff --check` | Procura erros de whitespace nos arquivos modificados. | **Aprovado**, sem saída de erro. |
| Testes focados de rota, catálogo e procedência | Exercitam telas, seleção de aeronaves, procedência, rota e PDF em cenários específicos. | **49 passaram** na execução focada. A suíte completa posterior também passou. |
| Testes visuais do shell | Verificam a casca visual, incluindo o logo nas páginas de autenticação. | **6 passaram** em `tests/test_casca_visual.py`. |
| Compilação Tailwind | Confirma que as classes CSS usadas pelos templates geram CSS válido. | `npm run css:build`: **aprovado**. |
| Inspeção visual do logo | Confere as páginas `/entrar` e `/cadastro` em larguras de 390 px e 1440 px. | Logo centralizado no cartão, sem cópia no cabeçalho dessas páginas e sem overflow horizontal; o cabeçalho autenticado mantém o logo. Largura renderizada observada: aproximadamente **86,39 px**, alvo de 86,4 px. |

### Como interpretar os números

- **136/136 testes** significa que todos os casos automatizados coletados foram aprovados nesta execução.
- **86,56% de cobertura** significa que essa proporção das instruções medidas foi executada. As linhas restantes não são automaticamente erros; podem pertencer a caminhos excepcionais ou ainda sem teste.
- **68,37% de mutação** supera o requisito de 56%. Os 161 mutantes sobreviventes são alterações artificiais que os testes não distinguiram; não significam 161 defeitos.
- Testes com fixtures verificam comportamentos de forma controlada e repetível. Eles não comprovam que um serviço externo esteja disponível nem que um conjunto real de dados esteja correto.

## Segurança e ambiente de teste

Os testes foram executados com a configuração descartável do projeto. Não foi feita conexão com banco de produção nem com o PostgreSQL específico `127.0.0.1:5434` citado na lista histórica de revisão. Os cenários automatizados de fontes externas usam fixtures; não foram usados dados reais ou credenciais de AISWEB, RAB, REDEMET ou OpenAIP.

## O que continua pendente

Os itens abaixo permanecem abertos porque exigem evidência que os testes automatizados não fornecem:

1. Obter e validar o extrato RAB vigente, sua unidade oficial de `NR_PMD` e fontes rastreáveis por aeronave/campo; ver [tarefas da rota e catálogo](../../specs/002-rota-com-escalas/tasks.md).
2. Completar testes de inelegibilidade sem data/aplicabilidade e a documentação sobre fontes secundárias, estimativas e conflitos; também registrados em [tarefas da rota e catálogo](../../specs/002-rota-com-escalas/tasks.md).
3. Validar edição, georreferenciamento, cobertura, licença e geração reproduzível de tiles da carta WAC. A carta permanece explicitamente indisponível até esses gates serem atendidos; ver [tarefas do mapa e radar](../../specs/009-mapa-interativo-carta-radar/tasks.md).
4. Fazer a validação manual de navegação, foco, teclado/toque e responsividade do mapa em 390 px e 1440 px; ver [tarefas OpenAIP](../../specs/010-camada-openaip/tasks.md) e [tarefas da tela por trecho](../../specs/013-plano-por-trecho/tasks.md).
5. Executar a revisão funcional de negócio descrita no backlog, que é diferente de cobertura de código; ver [revisão do código pronto](../../specs/revisao-codigo-pronto/tasks.md).

Os antigos quickstarts que exigiam uma base isolada `DATABASE_URL_DEMO` foram registrados como supersedidos pela arquitetura de banco único. Isso não significa que uma operação em banco DEMO tenha sido executada; ver [tarefas do catálogo DEMO](../../specs/006-catalogo-demo-sintetico/tasks.md) e [tarefas dos proxies DEMO](../../specs/007-proxies-aeronaves-demo/tasks.md).

## Conclusão

Os gates automatizados atuais estão verdes: suíte completa, cobertura mínima, mutação, forma dos módulos, lint e whitespace. As mudanças permanecem **sem commit** no workspace. As validações externas e manuais listadas acima não foram declaradas concluídas.
