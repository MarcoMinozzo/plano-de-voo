# Research: Aumentar logo no login

## Decisões

### Aumentar apenas o logo do login em 20%

- **Decisão**: Alterar a largura visível do logo no cartão de entrar de 86,4 px para 103,68 px; manter a imagem fluida em altura e centralizada.
- **Evidência**: `templates/entrar.html` e `templates/cadastro.html` atualmente declaram 86,4 px; a página de cadastro deve permanecer como está.
- **Racional**: 103,68 px é exatamente 20% maior que a dimensão atual e satisfaz o pedido sem alterar a escala das demais telas.
- **Alternativas consideradas**: Aumentar também o logo do cadastro ou mudar o logo do cabeçalho. Ambas ampliariam o escopo além do pedido.

### Reutilizar o teste visual e a compilação Tailwind existentes

- **Decisão**: Atualizar o teste visual de autenticação para verificar a nova dimensão do login e a dimensão preservada do cadastro; compilar Tailwind para gerar a classe de largura.
- **Evidência**: `tests/test_casca_visual.py` já verifica posição, texto alternativo, ausência no cabeçalho e largura atual; `static/css/input.css` procura classes nos templates.
- **Racional**: Cobrir diretamente a mudança e confirmar que o CSS produzido contém a nova regra.
- **Alternativas consideradas**: Adicionar uma nova biblioteca ou um sistema de estilo; desnecessário para um ajuste de dimensão.

## Questões em aberto

Nenhuma. O aumento foi interpretado como 20% sobre a largura atual do login.
