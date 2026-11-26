# Modelo de Dados: Integrar Tailwind CSS

Esta feature não altera dados de domínio, tabelas ou persistência PostgreSQL.

## Artefatos de estilo

| Artefato | Finalidade | Regra |
|---|---|---|
| Entrada Tailwind | Define tema e fontes de classes dos templates | Mantida em `static/css/input.css` |
| Folha compilada | CSS local consumido pelas páginas Flask | Gerada pelo build e versionada |
| Manifesto npm | Declara scripts e versões de ferramentas frontend | Lockfile fixa as dependências; pacotes não entram no runtime Python |

`node_modules/` é estado descartável de desenvolvimento, não dado do produto.
