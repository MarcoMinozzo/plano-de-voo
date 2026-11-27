# Modelo de dados — Camadas do mapa

Não há alteração no banco nem persistência do estado dos controles.

## Frame de satélite (resposta temporária)

| Campo | Tipo/validação | Uso |
|---|---|---|
| estado | `disponivel` ou `indisponivel` | Estado do resolvedor |
| provedor | Texto fixo `REDEMET` | Identificação visível da fonte |
| imagem_url | HTTPS, host oficial permitido | URL do PNG selecionado |
| hora_frame | Texto não vazio fornecido pela fonte | Identificação temporal visível |
| bounds.lat_min / lat_max | Número finito, entre -90 e 90; mínimo menor que máximo | Limites da imagem |
| bounds.lon_min / lon_max | Número finito, entre -180 e 180; mínimo menor que máximo | Limites da imagem |

O retorno público da aplicação não inclui a chave REDEMET, outros frames ou dados da API que não sejam necessários ao mapa.

## Estado da interface

- Satélite: desligado inicialmente; ao ativar, passa por carregando, disponível ou indisponível. Desativar remove apenas a camada de satélite.
- Radar: permanece independente e segue seu fluxo atual.
- WAC: documentos válidos abrem o diálogo atual; sem documentos, controle visível/desabilitado e estado de indisponibilidade.
- Rota: pontos existentes no plano; camada nenhuma os altera ou persiste.
