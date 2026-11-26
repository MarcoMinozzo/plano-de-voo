# Pesquisa: cartões de autenticação

## Decisões

### Aumentar cada logo em 50% sobre sua dimensão atual

- **Decisão**: usar 155,52 px no login e 129,6 px no cadastro, preservando a proporção da imagem.
- **Fundamento**: `templates/entrar.html` já usa 103,68 px e `templates/cadastro.html` 86,4 px. A especificação anterior confirma essas dimensões em `specs/017-aumentar-logo-login/spec.md`.
- **Alternativa considerada**: aplicar uma largura igual às duas páginas. Rejeitada porque “50% maior” se refere ao tamanho atual de cada cartão e os logos já têm dimensões distintas.

### Centralizar sem depender da altura do cabeçalho vazio

- **Decisão**: expor blocos substituíveis de cabeçalho e classes do conteúdo em `templates/base.html`; as duas telas públicas podem remover o cabeçalho vazio e centralizar seu cartão em uma área de altura mínima igual à viewport.
- **Fundamento**: o cabeçalho base reserva padding mesmo sem sessão; centralizar apenas dentro do `main` atual deslocaria o cartão. A tela deve continuar rolável verticalmente se o conteúdo não couber.
- **Alternativa considerada**: compensar a altura do cabeçalho com uma subtração fixa. Rejeitada por depender de altura implícita e mais frágil em alterações futuras.

### Dar mais respiro antes da ação de login

- **Decisão**: acrescentar ao botão “Acessar” um intervalo equivalente ao gap normal do formulário; com o gap atual de 0,6 rem, o espaço final fica aproximadamente duas vezes maior que os intervalos entre controles.
- **Fundamento**: o formulário em `templates/entrar.html` usa uma grade com gap uniforme de 0,6 rem.
- **Alternativa considerada**: aumentar o gap de todos os campos. Rejeitada porque a solicitação destaca somente a separação entre senha e ação.

### Preservar estrutura acessível

- **Decisão**: remover o título “Entrar” visualmente, mas conservar um título acessível com “Acessar”; manter texto visível no botão e o texto alternativo existente do logo.
- **Fundamento**: a remoção pedida é visual; controles e hierarquia semântica continuam úteis a leitores de tela.
- **Alternativa considerada**: remover todo título sem substituição. Rejeitada porque reduziria a navegação por cabeçalhos sem benefício visual adicional.

## Escopo técnico

Não há armazenamento, API externa ou nova dependência. As classes Tailwind são compiladas pela configuração existente; os testes de template verificam o conteúdo renderizado e as dimensões.
