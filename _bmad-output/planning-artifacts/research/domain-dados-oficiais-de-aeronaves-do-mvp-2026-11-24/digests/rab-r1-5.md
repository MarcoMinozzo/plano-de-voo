# Digest: situação de aeronavegabilidade no RAB

**Acesso:** 2026-11-24

## Conclusão

- **[23] A ANAC documenta `CD_INTERDICAO` como situação de aeronavegabilidade.** Entre os códigos descritos estão `N` (normal), `U` (ultraleve em situação normal), `Z` (experimental em situação normal), `R` (reserva de marcas), `S` (certificado suspenso), `C` (certificado cancelado), `V` (certificado vencido), `X` (aeronave interditada), `P` (situação punitiva) e `M` (matrícula cancelada). No CSV atual alguns registros trazem também o sufixo do motivo. **Confiança: alta para as definições publicadas pela ANAC. Classe: status regulatório.**

## Uso e ressalva

Para estimar frota, o usuário decidiu contar apenas `CD_INTERDICAO=N`. Embora a ANAC também descreva `U` e `Z` como situações normais para ultraleves e experimentais, respectivamente, esses códigos e todos os demais ficam fora da contagem do MVP. A lista preliminar anterior usava `N/U/Z` e precisa ser recalculada com `N` apenas. A classe avião e o PMD aprovado de até 5.670 kg continuam sendo filtros separados de elegibilidade.

## Fonte

23. ANAC, “Metadados - Registro Aeronáutico Brasileiro - RAB - Histórico”, modificado em 2026-03-19; acesso em 2026-11-24: https://www.gov.br/anac/pt-br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves-1/registro-aeronautico-brasileiro-historico/metadados-registro-aeronautico-brasileiro-historico

**Limite:** a documentação de valores e o CSV estão no ecossistema da mesma fonte oficial; a interpretação não foi confirmada por medição independente.
