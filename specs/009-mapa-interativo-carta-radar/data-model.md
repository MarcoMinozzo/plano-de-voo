# Data Model — Mapa interativo com carta e radar

Não há nova entidade persistente nem migração. O plano já guarda `meteorologia`, `carta` e `radar` em colunas JSON; a rota e os pontos dos aeródromos permanecem no servidor.

## Entidades e dados existentes

### Rota do plano

- **Origem**: `PlanoDeVoo.trechos`, com ICAO de saída e chegada; `app.py` resolve as coordenadas dos aeródromos e entrega os pontos ao template.
- **Regra**: a interface desenha somente os pontos calculados e não cria, interpola ou recalcula a rota.

### Boletim meteorológico

- **Origem**: `PlanoDeVoo.meteorologia`, contendo estados de plano, saída e destino.
- **METAR**: ICAO, texto `raw`, horário `hora`, temperatura `temp_c`, vento `vento_kt` e unidade `unidade_vento`, conforme disponível.
- **TAF**: texto `raw` e horário `hora`, conforme disponível.
- **Fonte**: Aviation Weather Center; ausência de plano, boletim ou campo continua explícita.

### Radar

- **Origem**: `PlanoDeVoo.radar`.
- **Campos usados**: `estado`, `url`, `hora`, `lat_min`, `lat_max`, `lon_min`, `lon_max` e `fonte`.
- **Regra**: renderizar apenas quando ativo pelo piloto e todos os dados de imagem/limites forem válidos.

### Candidata a carta WAC local

- **Persistência atual**: `PlanoDeVoo.carta` contém estado, URL documental e fonte AISWEB.
- **Estado da fonte**: GeoPDF oficial do AISWEB em avaliação; ainda não aprovado como camada cartográfica.
- **Evidência transitória necessária**: identificação da edição oficial, metadados de georreferenciamento, cobertura de todos os pontos da rota, termos autorizando conversão/cache/serviço de derivados e resultado da geração reproduzível de tiles em ambiente compatível.
- **Persistência de tiles**: não definida nem prevista antes da aprovação dos gates e de um plano revisado. Não gravar metadados presumidos nem alterar a tabela do plano.
- **Validação**: ausência do arquivo vigente, georreferenciamento inválido, cobertura incompleta, falta de autorização ou ambiente incompatível resulta em carta indisponível.

## Estado da interface

| Campo | Estado inicial | Transições |
|---|---|---|
| Base | `ruas` | `ruas` ↔ `carta`; carta só fica ativa após resposta válida e primeiro carregamento de tiles. |
| Radar | `desligado` | `desligado` ↔ `ligado` quando URL e quatro limites geográficos são válidos. |
| Carta | `indisponivel` até aprovação dos gates | `indisponivel` → `disponivel` somente após edição, cobertura, autorização e tiles válidos; erro de tile produz indisponibilidade. |

Trocar a base não altera o estado do radar; desligar radar não troca a base.
