# Quickstart: Validar Tailwind CSS

## Pré-requisitos

- Node.js 20 ou mais novo e npm.
- Dependências Python e banco configurados conforme `documentacao/operacao.md`.

## Instalar e compilar

Na raiz do repositório:

```bash
npm ci
npm run css:build
```

Resultado esperado: `static/css/tailwind.css` é gerado, inclui classes usadas
pelos templates Jinja e está disponível para o Flask servir localmente.

Durante alterações de estilo, use um segundo terminal:

```bash
npm run css:watch
```

Encerre o watcher após terminar. Ele não é necessário para executar o Flask.

## Verificar

```bash
uv run pytest --no-cov tests/test_casca_visual.py tests/test_tela_piloto.py tests/test_rota_pdf.py
git diff --check
```

Abra entrada, cadastro, plano novo, painel e plano calculado em largura móvel
(abaixo de 720 px) e desktop. Confirme a casca visual, os controles, as abas, a
ampulheta e o menu sem regressões; a folha deve carregar de `/static/`.
