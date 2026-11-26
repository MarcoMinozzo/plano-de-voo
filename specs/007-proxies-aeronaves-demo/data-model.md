# Data Model: Proxies de aeronaves DEMO

## Entidades existentes alteradas

### `FonteTecnicaAeronave`

Cada perfil mantém uma fonte selecionada por campo técnico. Acrescentar metadados opcionais para preservar registros oficiais existentes:

| Campo | Tipo | Regra |
| --- | --- | --- |
| `limite_inferior` | Float, anulável | Obrigatório para fonte sintética selecionada; mesma unidade de `valor` |
| `limite_superior` | Float, anulável | Obrigatório para fonte sintética selecionada; não menor que `limite_inferior` |
| `metodo_geracao` | Text, anulável | Obrigatório para fonte sintética selecionada |
| `versao_semente` | String(64), anulável | Identificador estável do conjunto/método de geração |
| `incerteza` | Text, anulável | Descreve a incerteza do valor e do intervalo |
| `justificativa_comparabilidade` | Text, anulável | Explica a aplicabilidade das fontes comparáveis ao proxy |

Para fontes sintéticas, `publicador` e `referencia` registram as fontes usadas; quando houver mais de uma, listar ambas. `modelo_variante` identifica o perfil alvo ou a variante comparável. `data_publicacao` permanece nula quando não há data editorial e `data_consulta` registra quando os dados foram preparados.

### `Aeronave` e `ExtratoRab`

- Preservar os 20 perfis genéricos existentes, atualizando os registros de procedência dos campos necessários.
- Criar até 20 perfis proxy com ligação ao extrato DEMO identificável como sintético.
- Perfis e fontes sintéticas permanecem inelegíveis quando `permitir_sintetica=False`; no modo normal não são exibidos nem aceitos.
- O limite do catálogo é 30 no modo normal e 40 no DEMO.

### `PlanoDeVoo`

Não alterar a forma de persistência do plano. O resultado deve manter o snapshot dos valores e da procedência usado no cálculo, de modo que alteração posterior da semente não reescreva o plano já criado. Marcar o resultado e o PDF como demonstração sintética.

### `EmendaRotaer` e `Aerodromo`

Não alterar o esquema. Provisionar apenas a emenda vigente oficial e os aeródromos vinculados, preservando o identificador da emenda. A operação não copia planos, pilotos nem demais dados da base normal. A aplicação DEMO exige uma emenda vigente oficial para criar o plano.

## Validações

- Para um campo sintético selecionado, `valor`, limites e unidade devem ser válidos; `limite_inferior <= valor <= limite_superior`.
- Limites, valor e intervalos devem ser finitos e positivos quando o campo exigir positividade.
- A evidência deve identificar publicador, referência e aplicabilidade; fontes secundárias comparáveis exigem justificativa.
- Peso máximo de decolagem deve exceder peso vazio; bagagem não pode exceder a carga útil admissível do perfil.
- Velocidade e consumo de cruzeiro devem pertencer ao mesmo perfil nominal.
- Campos obrigatórios não cobertos por evidência válida tornam o perfil inelegível; não substituir por defaults.
- Metadados novos são nulos para fontes oficiais já existentes e não mudam sua elegibilidade.

## Relações

```text
ExtratoRab (registro DEMO) 1 ── N Aeronave (perfis genéricos e proxies)
Aeronave 1 ── N FonteTecnicaAeronave (uma fonte selecionada por campo)
EmendaRotaer oficial vigente 1 ── N Aerodromo oficial
PlanoDeVoo ── snapshot do cálculo e procedência usados no momento da criação
```
