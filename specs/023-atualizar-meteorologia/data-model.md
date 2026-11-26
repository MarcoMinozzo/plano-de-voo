# Data Model: Atualizar meteorologia ao consultar o plano

## Entidades existentes utilizadas

### Plano de voo salvo

- **Origem e destino**: indicativos de aeródromos usados para consultar o radar da rota, conforme o comportamento existente.
- **Trechos**: sequência persistida que determina os aeródromos distintos cujos boletins são consultados.
- **Meteorologia e radar persistidos**: snapshot usado ao criar ou editar o plano; permanece intacto durante a consulta GET.

### Boletim meteorológico da resposta

- **Aeródromo**: indicativo ICAO do aeródromo consultado.
- **METAR**: texto original e campos estruturados fornecidos pela fonte.
- **TAF**: texto original quando disponível.
- **Fonte e horário**: valores da fonte quando fornecidos.
- **Estado**: disponível ou indisponível. Nenhum campo ausente é inferido.

### Resultado de radar da resposta

- **Imagem e cobertura**: URL e limites geográficos retornados pela REDEMET.
- **Fonte e horário**: identificação da fonte e horário quando fornecidos.
- **Estado e motivo**: disponível apenas com credencial, imagem e cobertura válidas; caso contrário, indisponível com motivo.

## Persistência e relações

Não são adicionadas entidades, colunas ou migrações. Os dados obtidos ao abrir o plano pertencem à resposta daquela requisição; não alteram a rota, os dados de voo ou os snapshots persistidos.
