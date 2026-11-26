# Plano de Implementação: Integrar Tailwind CSS

**Branch**: `main` | **Date**: 2026-11-25 | **Spec**: [spec.md](spec.md)

**Input**: Especificação em `specs/008-integrar-tailwind/spec.md`

## Summary

Adicionar Tailwind CSS CLI v4 para gerar uma folha local, detectar classes nos
templates Jinja e permitir que Flask sirva a saída estática sem Node em runtime.
Migrar os estilos atuais da casca para utilitários Tailwind, preservando a
aparência aprovada, os hooks semânticos existentes e os fluxos do piloto. Usar
somente dependências de desenvolvimento npm; não alterar dependências Python.

## Technical Context

**Language/Version**: CSS; Node.js 20.20.2 e npm 10.8.2 disponíveis no ambiente

**Primary Dependencies**: Tailwind CSS 4.3.5 e `@tailwindcss/cli` 4.3.5, travados em `package-lock.json`

**Storage**: Arquivos estáticos locais; nenhuma alteração no PostgreSQL

**Testing**: `npm ci`, `npm run css:build`, `uv run pytest --no-cov tests/test_casca_visual.py` e verificação visual no navegador

**Target Platform**: Aplicação Flask servida localmente; navegadores modernos

**Project Type**: Aplicação web server-rendered Flask/Jinja

**Performance Goals**: Nenhum processo Node no runtime; servir CSS compilado localmente

**Constraints**: Preservar a casca e todos os fluxos aprovados; nenhuma dependência Python nova; classes dinâmicas devem permanecer detectáveis; o CSS final deve estar disponível no repositório

**Scale/Scope**: Sete templates existentes, folha compartilhada e testes da casca; sem alteração em servidor, endpoints, dados ou cálculo

## Constitution Check

- **Cálculo e runtime Flask/PostgreSQL**: PASS — não muda lógica, banco nem runtime.
- **Dependências**: PASS — Tailwind é dependência de desenvolvimento frontend, justificada pelo objetivo; `requirements.txt` permanece inalterado.
- **Interface e idioma**: PASS — textos, conteúdo e identidade permanecem; só a implementação da apresentação migra.
- **Assets Tailwind**: PASS — a folha Tailwind será local, sem CDN ou requisição externa; integrações externas já existentes, como Leaflet, permanecem inalteradas.
- **Observabilidade e fluxo**: PASS — não muda navegação, permissões, planejamento ou impressão.

## Research Decisions

- Tailwind CLI em vez de Vite/PostCSS: a aplicação não tem bundler frontend e só precisa de CSS estático; CLI minimiza infraestrutura.
- Tailwind CSS v4.3.5: documentação oficial recomenda instalar `tailwindcss` e `@tailwindcss/cli` e compilar `input.css` para uma folha estática.
- Registrar `templates/` como fonte de classes: os templates Jinja contêm classes condicionais; nomes completos devem existir no texto fonte para detecção estática.
- Importar tema e utilitários sem Preflight: evitar o reset global que remove margens e estilos de headings/listas, reduzindo regressões durante a migração visual.
- Manter `static/css/tailwind.css` versionado: o Flask deve servir o asset mesmo quando Node/npm não estiverem instalados no ambiente de execução.
- Fontes: [Tailwind CLI installation](https://tailwindcss.com/docs/installation/tailwind-cli), [Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files) e [Preflight](https://tailwindcss.com/docs/preflight).

## Project Structure

### Documentation

```text
specs/008-integrar-tailwind/
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source Code

```text
package.json
package-lock.json
.gitignore
static/css/
├── input.css
└── tailwind.css
templates/
├── base.html
└── páginas Jinja existentes
tests/test_casca_visual.py
documentacao/operacao.md
```

**Structure Decision**: Manter o CSS fonte e compilado em `static/css/`, junto
dos assets servidos pelo Flask. `package.json` e lockfile controlam somente o
build frontend; `node_modules/` fica local e ignorado pelo Git.

## Constitution Check (Post-Design)

- **Sem nova dependência de runtime Python ou banco**: PASS.
- **Build reproduzível e asset local sem watcher obrigatório**: PASS.
- **Preservação visual com validação funcional e responsiva**: PASS.
- **Escopo restrito à apresentação e documentação operacional**: PASS.

## Complexity Tracking

Sem violações da constituição ou nova camada de runtime a justificar.
