---
title: 'Ajustes visuais nas telas de autenticação'
type: 'feature'
created: '2026-11-26'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'ea93b379a269fe0bea87602c8bc005c5763a3fbe'
context:
  - '{project-root}/.specify/memory/constitution.md'
  - '{project-root}/.cursor/rules/speckit-sdd.mdc'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Os cartões de entrar e criar acesso precisam de maior destaque e centralização na viewport. A tela de entrar também deve retirar a palavra “Entrar” e mostrar a atribuição de autoria e direitos solicitada.

**Approach:** Aumentar em 50% o logo de cada cartão em relação às dimensões atuais, centralizar os dois cartões vertical e horizontalmente, remover o título visível “Entrar”, renomear o botão para “Acessar”, dar ao espaço entre a senha e esse botão o dobro do intervalo normal entre os controles e exibir abaixo do link “Criar acesso” a frase “Sistema Desenvolvido por Machina Sapiens - Todos os Direitos Reservados - 2026”, em branco e tamanho pequeno.

## Boundaries & Constraints

**Always:** Manter a proporção e o texto alternativo do logo; conservar campos, validação, links e envio dos formulários; manter os cartões contidos em viewports móveis e desktop; usar texto em português; aumentar o intervalo somente entre a senha e o botão de login, sem desalinhar a cadência vertical dos demais controles.

**Never:** Alterar autenticação, sessões, persistência, rotas ou conteúdo de outras telas; remover ou inutilizar a ação de envio do login; criar banco de dados ou dependência nova.

</frozen-after-approval>

## Code Map

- `templates/entrar.html` — cartão de login; logo atualmente com 103,68 px, título “Entrar”, botão de envio e link “Criar acesso”.
- `templates/cadastro.html` — cartão de cadastro; logo atualmente com 86,4 px e formulário existente.
- `templates/base.html` — cabeçalho vazio nas telas sem sessão e contêiner principal; pode precisar expor classes/layout para centralizar o cartão sem deslocar outras telas.
- `static/css/input.css` e `static/css/tailwind.css` — estilos-fonte e folha compilada local já usados pela aplicação.
- `tests/test_casca_visual.py` — verifica dimensões e posição dos logos; atualizar para 155,52 px no login e 129,6 px no cadastro e acrescentar asserções de centralização e atribuição.
- `specs/017-aumentar-logo-login/spec.md` e `specs/016-logo-login-cadastro/tasks.md` — decisões anteriores de dimensão, proporção e ausência do logo no cabeçalho.
- `_bmad-output/planning-artifacts/ux-designs/ux-Plano de voo-2026-11-24/DESIGN.md` — define o cartão de vidro e o emblema, com largura máxima de 168 px.

## Tasks & Acceptance

**Execution:**
- [x] `tests/test_casca_visual.py` — cobrir dimensões dos dois logos, alinhamento dos cartões, presença/estilo da frase de autoria e espaçamento reforçado antes de alterar os templates.
- [x] `templates/base.html`, `templates/entrar.html` e `templates/cadastro.html` — centralizar os cartões na viewport e aplicar a composição definida, preservando o comportamento dos formulários.
- [x] `static/css/tailwind.css` — recompilar a folha local se a implementação introduzir utilitários novos.

**Acceptance Criteria:**
- Given a página `/entrar`, when o cartão é exibido, then o título “Entrar” não aparece e o botão de envio é identificado como “Acessar”.
- Given a página `/entrar`, when o cartão é exibido, then o logo mede 155,52 px, mantém proporção e o cartão fica centralizado na viewport.
- Given a página `/cadastro`, when o cartão é exibido, then o logo mede 129,6 px, mantém proporção e o cartão fica centralizado na viewport.
- Given a tela de login, when o link “Criar acesso” é exibido, then a frase solicitada aparece logo abaixo, em branco e fonte pequena.
- Given uma viewport de 390 px ou 1440 px, when qualquer cartão de autenticação é exibido, then não há overflow horizontal e os campos e ações permanecem acessíveis.
- Given o formulário de login, when os controles são exibidos, then o intervalo entre senha e “Acessar” é cerca de duas vezes o intervalo normal entre os controles adjacentes.
- Given o usuário envia o formulário de login, when os dados estão válidos, then o botão “Acessar” mantém o envio funcional.

## Implementation Notes

Sem migração, alteração de dados ou integração externa. A verificação visual deve cobrir `/entrar` e `/cadastro` nas larguras de 390 px e 1440 px.

- Implementados logos 50% maiores, cartões centralizados, título visível removido, botão “Acessar”, atribuição e intervalo de senha/ação dobrado.
- Verificação: 23 testes focados passaram; Playwright confirmou centralização e ausência de overflow em 390 px e 1440 px, e rolagem vertical funcional em viewport baixa.

## Spec Change Log

- O usuário acrescentou aumentar o espaço entre a senha e o botão “Acessar”; incluído como o dobro do intervalo normal dos demais controles do formulário.

## Review Triage Log
