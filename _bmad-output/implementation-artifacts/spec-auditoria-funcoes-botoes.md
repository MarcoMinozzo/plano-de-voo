---
title: 'Auditoria de funções, botões e camadas'
type: 'bugfix'
created: '2026-11-26'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/.cursor/rules/speckit-sdd.mdc'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** O piloto relata ações que parecem não responder, especialmente salvar o nome de exibição e controlar as camadas do mapa. A inspeção inicial indica que o nome é gravado, mas não há confirmação visual; as abas e a base de ruas funcionam, enquanto WAC, OpenAIP e radar estão indisponíveis por gates ou configuração.

**Approach:** Auditar os fluxos de ações e controles visíveis, confirmar cada resultado com testes ou navegação não destrutiva e corrigir somente falhas reproduzíveis. Tornar explícito o resultado do salvamento e o motivo real de indisponibilidade das camadas, preservando todos os gates técnicos e legais; entregar um resumo dos controles verificados e dos bloqueios externos.

**Boundaries & Constraints**

**Always:** Preservar dados existentes e alterações locais; não enviar formulários reais durante a auditoria; verificar as rotas pelo piloto autenticado; manter as mensagens em português; distinguir falha de código de camada sem chave, cobertura ou validação; usar somente estados e respostas reais; em telas estreitas, conter a rolagem da tabela larga sem ocultar colunas nem expandir a página inteira.

**Never:** Habilitar WAC sem edição, georreferenciamento, cobertura e autorização validados; substituir carta por ruas ou OpenAIP; desenhar radar sem limites válidos; persistir chaves; criar migração ou banco; alterar cálculos, sessão, plano ou dados de piloto para fins de teste; remover avisos didáticos existentes.

## I/O & Edge-Case Matrix

| Cenário | Entrada / estado | Resultado esperado | Tratamento |
|---|---|---|---|
| Salvamento do nome | Nome válido no perfil | Valor permanece gravado e a tela confirma a conclusão | Erro de validação continua visível; não exibir sucesso |
| Base do mapa | Plano com ao menos dois pontos | Mapa de ruas e rota carregam; alternar trecho mantém uma única aba selecionada | Tiles cancelados durante reposicionamento não são tratados como falha persistente |
| Camada indisponível | WAC, OpenAIP ou radar sem gate/configuração | Controle permanece indisponível e informa a causa observada | Não ativar fallback nem mascarar indisponibilidade |
| Outros controles | Formulários, navegação e ações sem alteração de dados | Resultado corresponde ao handler e aos testes existentes | Não executar logout, cálculo ou impressão que altere sessão/dados sem necessidade |

</frozen-after-approval>

## Code Map

- `templates/entrar.html`, `templates/cadastro.html`, `templates/painel.html`, `templates/plano_novo.html`, `templates/plano.html` e `templates/perfil.html` — superfícies com ações e navegação a conferir.
- `app.py` e `servidor/planos.py` — handlers de conta, perfil, navegação e planos; `tests/test_acesso.py` cobre persistência, validação e isolamento do perfil.
- `templates/plano.html` — abas, mapa e controles de camadas; no navegador as abas alternaram corretamente, uma por vez, e 9/9 tiles do mapa base carregaram.
- `servidor/tempo.py` e `servidor/openaip.py` — estados e requisitos de fontes externas; não habilitar camada sem configuração/validação. `tests/test_tempo.py` e `tests/test_tela_piloto.py` cobrem fontes e estados.
- No viewport de 390 px, o documento mediu 1261 px de largura por causa de uma tabela de 11 colunas; conter sua rolagem em `templates/plano.html` sem perder dados.
- `tests/review/test_module_shape.py` — a suíte completa teve 137 aprovações e uma falha de complexidade em `servidor/pdf_plano.py`; registrar o resultado sem atribuir causa nem ampliar esta entrega.

## Tasks & Acceptance

**Execution:**
- [ ] `app.py`, `templates/perfil.html`, `tests/test_acesso.py` — comunicar sucesso após salvar o próprio nome e cobrir erro/sucesso sem alterar o isolamento.
- [ ] `templates/plano.html`, `servidor/tempo.py`, `servidor/openaip.py`, `tests/test_tela_piloto.py`, `tests/test_tempo.py` — apresentar causa verificável para cada camada indisponível, sem mudar os gates.
- [ ] `templates/plano.html`, `tests/test_tela_piloto.py` — conter a tabela de 11 colunas em sua própria área rolável e confirmar que a página não excede a viewport de 390 px.
- [ ] `templates/entrar.html`, `templates/cadastro.html`, `templates/painel.html`, `templates/plano_novo.html`, `templates/plano.html`, `templates/perfil.html`, `tests/test_acesso.py`, `tests/test_tela_piloto.py`, `tests/test_rota_pdf.py` — conferir formulários, navegação, abas, zoom, impressão e saída; relatar cobertura e bloqueios sem efetuar ações destrutivas.
- [ ] `documentacao/piloto.md` — atualizar somente instruções diretamente afetadas, se necessário.

**Acceptance Criteria:**
- Given um nome válido, when o piloto salva, then a tela confirma o sucesso somente após persistência e preserva validação e isolamento.
- Given uma camada sem chave, validação ou cobertura, when o piloto consulta o mapa, then a causa disponível é informada e a camada permanece desligada.
- Given a base de ruas e uma rota válida, when o piloto troca de trecho ou usa os controles disponíveis, then a rota permanece visível e uma única aba fica selecionada.
- Given a página do plano em uma viewport de 390 px, when a tabela larga é exibida, then somente a área da tabela rola horizontalmente e a página permanece dentro da viewport.
- Given todos os controles auditados, when os testes focados e a navegação não destrutiva são concluídos, then cada ação tem resultado verificado ou bloqueio explicitado no relatório.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest --no-cov tests/test_acesso.py tests/test_tela_piloto.py tests/test_tempo.py` — testes focados aprovados.
- `uv run pytest -q` — suíte completa; registrar falhas observadas fora do escopo sem atribuir causa sem evidência.

**Manual checks:**
- Verificar perfil, plano e camadas na aplicação autenticada sem enviar alterações a dados reais; validar abas, mapa base, estados indisponíveis e ausência de overflow da página em 390 px e 1440 px.
