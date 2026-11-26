# Interação do mapa e apresentação meteorológica

## Camadas

- Exibir no topo do quadro controles mutuamente exclusivos para **Mapa de ruas** e **Carta de voo visual**; ruas iniciam selecionadas.
- O radar inicia desligado. O botão **Radar de chuva** controla somente o overlay: pode ser ligado ou removido sobre qualquer base sem perder a rota nem trocar de base.
- A carta usa GeoAISWEB/GeoServer WMS oficial. Confirmar a disponibilidade e a camada WAC aplicável. Se carta ou radar estiver indisponível, informar claramente; não usar uma substituição silenciosa nem um overlay sem limites geográficos válidos.
- Preservar rota, zoom e controles acessíveis por toque e teclado. Desenhar somente pontos e trechos calculados pelo servidor.

## Meteorologia

- Organizar METAR/TAF por aeródromo e tipo de boletim, com rótulos técnicos e campos retornados pela fonte.
- Exibir fonte e horário quando fornecidos e manter o texto bruto do boletim identificável. Indicar campos ausentes como indisponíveis; não inferir nem interpretar valores.

## Casos de aceitação

| Estado | Resultado esperado |
|---|---|
| Duas bases e radar disponíveis | Alternar base e radar independentemente; rota permanece visível. |
| Carta indisponível | Informar indisponibilidade; não apresentar ruas como carta. |
| Radar indisponível ou sem limites válidos | Overlay não desenhado e estado indisponível visível. |
| METAR/TAF ausente | Identificar boletim/campo indisponível sem completar valores. |
| Menos de dois pontos de rota | Não desenhar um mapa sem rota mapeável. |

## Áreas do código e validação

- `templates/plano.html`: controles, mapa Leaflet, rota e apresentação dos boletins.
- `servidor/tempo.py`: dados AWC METAR/TAF, radar MaxCappi REDEMET e carta WAC AISWEB/GeoAISWEB.
- `servidor/planos.py`: persistência das fontes e entrega dos pontos calculados.
- `tests/test_tempo.py`, `tests/test_tela_piloto.py`: cobertura de fontes, estados e interface.
- `documentacao/piloto.md`: instruções curtas para controles e indisponibilidades.
- Verificar em 390 px e 1440 px, incluindo alternância de base, overlay independente, rota, zoom, METAR/TAF e falhas explícitas.

As referências visuais e comportamentais adotadas estão em `DESIGN.md` e `EXPERIENCE.md`, listadas como companions no SPEC.
