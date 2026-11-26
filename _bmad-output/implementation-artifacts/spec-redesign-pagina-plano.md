---
title: 'Redesign da página do plano'
type: 'feature'
created: '2026-11-26'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '06d4e5de2e3d94f9abba45e0490bc7618a1e90db'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/EXPERIENCE.md'
  - '{project-root}/specs/009-mapa-interativo-carta-radar/'
  - '{project-root}/specs/024-camada-radar-rainviewer/'
  - '{project-root}/specs/025-enxugar-pagina-plano/'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A página do plano dispersa informações, mostra aeródromos principalmente por siglas e confunde alertas e camadas meteorológicas. A máscara visual do RainViewer cobre grandes áreas do mapa e reduz a legibilidade da rota.

**Approach:** Reorganizar a página em um card principal responsivo, priorizando a rota completa, fichas legíveis, alertas destacados e controles compactos dentro do mapa. Melhorar as camadas sem alterar a rota nem ocultar estados e créditos obrigatórios.

## Boundaries & Constraints

**Always:** Preservar a marca, usar cerca de 80% da largura em telas largas e adaptar para telas estreitas. Exibir nomes completos nas fichas e ICAO nos títulos/abas. Destacar alertas de limites em vermelho e texto. Preservar rota calculada no servidor e aviso didático. Ruas iniciam ativas; Google Maps fica desativado até configurar chave local. REDEMET permanece oficial e independente; RainViewer, se ativo, permanece suplementar, com crédito, horário e aviso conciso de cobertura. Manter a WAC marcada como indisponível até passar os critérios de validação; retirar OpenAIP da seleção enquanto não estiver configurado. Contatos vêm somente do AISWEB/ROTAER quando publicados; ausência deve ser explícita.

**Never:** Inventar dados ou contatos; apresentar mapas como carta WAC; substituir REDEMET por RainViewer; ocultar créditos ou indisponibilidade; alterar cálculo, dados da rota, acesso ou PDF. Remover “Como ler este plano” e o link de PDF do rodapé, mantendo impressão no topo.

## I/O & Edge-Case Matrix

| Cenário | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Rota | Plano com escalas | Rota completa e nomes oficiais nas fichas | Não inventar nomes |
| Aeródromos finais | Dados ROTAER e contatos publicados ou ausentes | Mostrar nome, ICAO, tipo, coordenadas, elevação, edição/data e contato disponível | Marcar campo ausente sem estimativa |
| Alertas | Limite excedido no resultado | Alerta vermelho e textual | Preservar mensagem original |
| Camadas | Google sem chave; radar disponível/indisponível | Controles internos compactos; ruas ativas; radar separado | Informar indisponibilidade sem fallback |
| RainViewer | Camada suplementar ativa | Base legível; crédito, horário e aviso conciso de cobertura | Remover camada inválida e informar |

</frozen-after-approval>

## Code Map

- `templates/plano.html` -- resumo, fichas e mapa Leaflet; a máscara RainViewer usa tiles opacos (`opacity: 0.4`), enquanto REDEMET usa imagem e limites geográficos.
- `app.py:ver_plano` -- já resolve `aerodromos_rota`, mas envia ao template apenas os pontos.
- `servidor/modelos.py:Aerodromo` e `servidor/rotaer_parse.py:_detalhe_rotaer_html` -- dados ROTAER de nome/localização; sem persistência de contato.
- `servidor/tempo.py:radar`, `servidor/rainviewer.py` e rotas autenticadas em `app.py` -- camadas oficiais/suplementares existentes; preservar a independência e validação.
- `tests/test_tela_piloto.py`, `tests/test_tempo.py`, `tests/test_catalogo_aerodromos.py` -- testes de tela, radar e catálogo; `documentacao/piloto.md` -- orientação ao piloto.

## Tasks & Acceptance

**Execution:**
- [ ] `app.py` e `templates/plano.html` -- enviar dados dos aeródromos e reorganizar rota, fichas, alertas e mapa no card responsivo.
- [ ] `servidor/modelos.py`, `servidor/rotaer_parse.py` e migração Alembic -- persistir contatos AISWEB/ROTAER publicados; representar os ausentes como indisponíveis.
- [ ] `templates/plano.html` -- criar controles compactos, Google desativado sem chave e corrigir a máscara RainViewer.
- [ ] Testes focados em `tests/test_tela_piloto.py`, `tests/test_tempo.py` e `tests/test_catalogo_aerodromos.py`; atualizar `documentacao/piloto.md`.

**Acceptance Criteria:**
- Given qualquer viewport, when o piloto consulta um plano, then vê um card responsivo com rota completa, nomes por trecho, alertas textuais em vermelho e sem a orientação/ação PDF do rodapé.
- Given Google Maps sem chave ou radar indisponível, when o piloto usa o mapa, then os controles indicam corretamente o estado e não simulam outra fonte.
- Given qualquer radar ativo, when o mapa é exibido, then a sobreposição fica alinhada à geografia e a base permanece legível; RainViewer mantém crédito, horário e aviso de cobertura sem substituir REDEMET.
- Given contato ausente na fonte escolhida, when um aeródromo é exibido, then a ausência fica clara e nenhum contato é inventado.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Manter blueprint, azul-marinho, vidro, papel claro, amarelo de ação e tipografia sem serifa. O card externo agrupa as superfícies; o limite de 48 rem cede à largura de 80% solicitada. Controles acessíveis distinguem estado sem depender da cor. O estado desligado é implícito; indisponibilidade, crédito e horário aparecem em forma compacta.

## Verification

**Commands:**
- `uv run pytest --no-cov tests/test_tela_piloto.py tests/test_tempo.py tests/test_catalogo_aerodromos.py` -- esperado: cenários de interface, camada e catálogo aprovados.
- `git diff --check` -- esperado: sem erros de whitespace.

**Manual checks:**
- Confirmar layout em 390 px e 1440 px, nomes e alertas, controles por teclado/toque, visibilidade da rota e legibilidade do mapa com cada camada ligada/desligada.
