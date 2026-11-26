# Research: Logo centralizado no login e cadastro

## Decisões

### Reutilizar o emblema existente e manter o cabeçalho fora do fluxo de autenticação

- **Decisão**: Usar o mesmo arquivo de emblema já exibido no cabeçalho. Renderizá-lo no cartão de entrar e cadastro, centralizado antes do título, com 86,4 px de largura. O cabeçalho não deve duplicá-lo nessas telas; nas telas autenticadas permanece igual.
- **Evidência**: `templates/base.html` contém o emblema atual com largura de 72 px; `templates/entrar.html` e `templates/cadastro.html` estendem esse layout e já têm um cartão principal.
- **Racional**: Reutiliza o asset e mantém a mudança limitada à composição visual solicitada.
- **Alternativas consideradas**: Criar outro asset ou remover o emblema do cabeçalho em todas as páginas. A primeira duplica recursos; a segunda altera páginas fora do escopo.

### Manter os formulários e a acessibilidade existentes

- **Decisão**: Preservar `alt="Plano de voo"`, a proporção original, os campos, mensagens e rotas atuais.
- **Evidência**: Os templates atuais já fornecem o texto alternativo e o layout responsivo com Tailwind.
- **Racional**: A solicitação altera posição e dimensão, não o conteúdo ou comportamento da autenticação.
- **Alternativas consideradas**: Alterar título ou elementos do formulário; não é necessário para atender ao pedido.

## Questões em aberto

Nenhuma. A dimensão de referência de 72 px e a restrição do cabeçalho às duas páginas foram confirmadas no contexto do pedido e no código atual.
