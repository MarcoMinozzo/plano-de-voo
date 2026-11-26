# Verificação independente: interpretação do esquema RAB

**Acesso:** 2026-11-24 · validação normal

- **`CD_TIPO`:** a definição como habilitação/treinamento de piloto está explícita na página de metadados ANAC. Não foi encontrada confirmação semântica independente; o repositório de terceiros consultado confirma apenas que a coluna existe. **Status: não verificado independentemente; confiança alta na descrição da ANAC.**
- **`CD_CLS`:** os metadados ANAC descrevem classificação ligada a características e ao RBAC 21; o RBAC 21 atual trata de certificação de projeto, mas não confirma diretamente o mapeamento do campo. **Status: parcialmente verificado; confiança média/alta.**
- **`DS_MODELO`:** os metadados ANAC descrevem modelo reconhecido por certificação; a IS 21-001B também trata de certificados de tipo e especificações que contêm modelos, sem validar cada valor do CSV. **Status: verificado com ressalva; confiança alta.**
- **`NR_PMD`:** a ANAC define o rótulo como peso máximo de decolagem. Não foi localizada fonte que declare explicitamente a unidade do campo do CSV; documentos ANAC usam kg para limites de PMD, mas isso não prova a unidade desse campo. **Status: conceito verificado, unidade não verificada; confiança média.**
- **Titulares e operadores:** a descrição ANAC confirma nomes/razões sociais e identificadores de documento. As confirmações externas encontradas dependem do próprio conjunto ANAC. **Status: verificado pela fonte primária; confiança alta.**

## Fontes adicionais

7. ANAC, RBAC 21, modificado em 2026-10-22: https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-21
8. ANAC, IS 21-001B, modificada em 2024-11-22: https://www.anac.gov.br/assuntos/legislacao/legislacao-1/iac-e-is/is/is-21-001
9. ANAC, Resolução nº 686, de 2022-07-13: https://pergamum.anac.gov.br/pergamum/vinculos/RA2022-0686.pdf
10. ANAC, “Drones de Classe 1”, modificada em 2026-07-31: https://www.gov.br/anac/pt-br/assuntos/regulados/aviacao-geral/drones/drones-de-classe-1-peso-maximo-de-decolagem-superior-a-150-kg
11. ANAC, Consulta ao RAB: https://aeronaves.anac.gov.br/aeronaves/cons_rab_resposta.asp
12. Primeflight, wrapper de consulta RAB: https://github.com/primeflight/rab

## Consequência

Usar apenas o CSV como fonte de contagem, sem tomar `CD_TIPO` por tipo de aeronave. Não filtrar nem comparar PMD numérico em kg até confirmar a unidade do campo ou validar os valores com documentos oficiais. Titulares e operadores ficam fora de qualquer agregação exportada.
