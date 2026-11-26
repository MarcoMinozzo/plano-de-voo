# Pesquisa: Integrar Tailwind CSS

## Decisões

- Usar Tailwind CSS CLI 4.3.5 e `@tailwindcss/cli` 4.3.5, instalados como dependências de desenvolvimento e fixados no lockfile npm.
- Criar uma entrada CSS local e compilar para `static/css/tailwind.css`; não usar CDN para Tailwind nem carregar Node durante as requisições Flask. Integrações externas já existentes permanecem fora do escopo.
- Detectar as classes em `templates/` com `@source`, relativo à folha de entrada. Manter cada token de classe completo nos templates; não formar nomes concatenando fragmentos Jinja.
- Importar as camadas de tema e utilitários sem a camada Preflight. Isso permite usar classes Tailwind sem remover estilos padrão que hoje contribuem para a aparência.
- Versionar a folha compilada para disponibilizar a aplicação sem etapa de build em seu runtime; ignorar `node_modules/`.
- Migrar o CSS compartilhado e específico para classes utilitárias, preservando classes semânticas usadas por testes, JavaScript e componentes externos.

## Fundamentação

A documentação oficial descreve o CLI como opção simples para compilar templates
em CSS estático: instala `tailwindcss` junto de `@tailwindcss/cli`, importa
Tailwind no CSS de entrada e gera uma saída consumida pela página. A detecção
estática lê arquivos como texto, portanto fontes Jinja devem conter as classes
completas. A configuração explícita `@source` resolve o caminho de templates
relativo ao CSS e não depende de descoberta implícita do diretório de execução.

A documentação de Preflight confirma que o import completo altera defaults
globais, inclusive margens e headings. Como a meta é preservar a casca já
aprovada, o plano usa tema/utilitários sem Preflight durante a migração.

## Alternativas consideradas

- **Vite**: não adotado, pois o projeto não possui bundler, módulos frontend ou JavaScript que precisem de pipeline.
- **Tailwind CDN**: rejeitado; não garante asset local nem build reproduzível e adicionaria dependência externa ao carregamento da interface.
- **Preflight habilitado**: rejeitado nesta migração, pois pode alterar defaults que não estão explicitamente estilizados.
- **Deixar estilos inline e adicionar apenas a ferramenta**: rejeitado após a decisão do piloto de migrar o CSS atual para classes Tailwind.

## Fontes

- Tailwind Labs, [Tailwind CLI installation](https://tailwindcss.com/docs/installation/tailwind-cli), acessada em 2026-11-25.
- Tailwind Labs, [Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files), acessada em 2026-11-25.
- Tailwind Labs, [Preflight](https://tailwindcss.com/docs/preflight), acessada em 2026-11-25.
- npm Registry: `tailwindcss` e `@tailwindcss/cli` versão 4.3.5, consultado em 2026-11-25; `node --version` 20.20.2 e `npm --version` 10.8.2 no ambiente.
