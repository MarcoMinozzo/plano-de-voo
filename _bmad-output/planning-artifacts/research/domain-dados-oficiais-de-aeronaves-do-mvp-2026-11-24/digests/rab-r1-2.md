# Digest: interpretação do esquema RAB — rodada 1

**Acesso:** 2026-11-24

## Conclusões verificadas

- **[6] `CD_TIPO` não é uma classificação geral de aeronave.** A documentação da ANAC o define como treinamento e habilitação de pilotos para modelos correspondentes. A classificação relevante para agrupamentos é `CD_CLS`, descrita como baseada em características como tipo de pouso e tipo/número de motores, prevista no RBAC 21. **Confiança: alta. Classe: interpretação de esquema.**
- **[7] O RAB identifica o modelo certificado e seus dados de registro.** A ANAC define `DS_MODELO` como modelo de produto aeronáutico reconhecido por certificação pela Agência e `NR_PMD` como peso máximo de decolagem. A página não declara a unidade de `NR_PMD`; confirmar unidade por documentação oficial antes de usar seu valor numérico. `TP_POUSO` distingue, entre outros, helicóptero, pouso convencional e água; `TP_MOTOR` e `QT_MOTOR` trazem informações úteis para classificar candidatos. **Confiança: alta para os rótulos, média para aplicar a documentação histórica ao CSV atual. Classe: interpretação de esquema.**
- **[8] O CSV contém dados de titulares e operadores.** A documentação descreve nomes/razões sociais e números de documentos (CPF anonimizado ou CNPJ) nas colunas correspondentes. Não importar nem expor essas colunas; produzir apenas agregados técnicos por modelo. **Confiança: alta. Classe: privacidade.**

## Fontes

6. ANAC, “Metadados - Registro Aeronáutico Brasileiro - RAB - Histórico”, modificado em 2026-03-19; acesso em 2026-11-24: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro-historico/metadados-registro-aeronautico-brasileiro-historico

## Implicações e lacunas

- Não usar `CD_TIPO` para separar aviões, helicópteros e outras aeronaves.
- Verificar os valores reais de `CD_CLS`, `TP_POUSO`, `TP_MOTOR` e `CD_INTERDICAO` no CSV atual, sem ler nem registrar dados de proprietário/operador.
- Encontrar fonte oficial para a unidade de `NR_PMD` e confirmar os critérios de aeronavegabilidade/registro que devem compor a contagem de frota.
- A tabela auxiliar de categorias de homologação por modelo e o guia do RAB são próximos documentos a verificar.
